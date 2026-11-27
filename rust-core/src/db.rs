use crate::models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    GradeCategory, ImportReport, MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary,
    SavedContact, StudentAttendanceRow, StudentGradeRow, TopStudentCount,
};
use crate::persian::{
    format_iso_to_jalali, format_jalali_month_label, grade_rank, is_middle_grade,
    jalali_month_range_iso, normalize_mobile, normalize_national_id, normalize_persian,
    persian_sort_key,
};
use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::time::{SystemTime, UNIX_EPOCH};

const DEFAULT_GRADE_CATEGORIES: [&str; 9] = [
    "مستمر مهر", "مستمر آبان", "مستمر آذر", "مستمر دی",
    "پودمان ۱", "پودمان ۲", "پودمان ۳", "پودمان ۴", "پودمان ۵",
];

pub fn init_database(db_path: &str) -> Result<Connection, CoreError> {
    let conn = if db_path == ":memory:" { Connection::open_in_memory() } else { Connection::open(db_path) }
        .map_err(|e| CoreError::Database(e.to_string()))?;

    conn.execute_batch(
        "PRAGMA journal_mode = WAL; PRAGMA synchronous = NORMAL; PRAGMA foreign_keys = ON;
         PRAGMA temp_store = MEMORY; PRAGMA cache_size = -4000;

         CREATE TABLE IF NOT EXISTS students (
             id INTEGER PRIMARY KEY AUTOINCREMENT, row_num INTEGER NOT NULL, school_name TEXT NOT NULL,
             major TEXT NOT NULL, grade TEXT NOT NULL, section INTEGER NOT NULL,
             first_name TEXT NOT NULL, last_name TEXT NOT NULL, father_name TEXT NOT NULL,
             national_id TEXT NOT NULL UNIQUE, mobile TEXT NOT NULL, search_key TEXT NOT NULL
         );

         CREATE TABLE IF NOT EXISTS attendance (
             student_id INTEGER NOT NULL, date_iso TEXT NOT NULL,
             period INTEGER NOT NULL CHECK(period BETWEEN 1 AND 4),
             status INTEGER NOT NULL, exit_time TEXT NOT NULL DEFAULT '',
             note TEXT NOT NULL DEFAULT '', teacher_name TEXT NOT NULL DEFAULT '',
             lesson_name TEXT NOT NULL DEFAULT '', class_time TEXT NOT NULL DEFAULT '',
             updated_at INTEGER NOT NULL,
             PRIMARY KEY (student_id, date_iso, period),
             FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
         );

         CREATE TABLE IF NOT EXISTS grade_categories (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL UNIQUE,
             sort_order INTEGER NOT NULL DEFAULT 0
         );

         CREATE TABLE IF NOT EXISTS student_grades (
             student_id INTEGER NOT NULL, category_id INTEGER NOT NULL,
             score TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', updated_at INTEGER NOT NULL,
             PRIMARY KEY (student_id, category_id),
             FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
             FOREIGN KEY (category_id) REFERENCES grade_categories(id) ON DELETE CASCADE
         );

         CREATE TABLE IF NOT EXISTS saved_contacts (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL, role TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL UNIQUE
         );

         CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
         CREATE INDEX IF NOT EXISTS idx_students_class ON students(major, grade, section);
         CREATE INDEX IF NOT EXISTS idx_students_search ON students(search_key);
         CREATE INDEX IF NOT EXISTS idx_att_dp ON attendance(date_iso, period, student_id);",
    ).map_err(|e| CoreError::Database(e.to_string()))?;

    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN exit_time TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN teacher_name TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN lesson_name TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN class_time TEXT NOT NULL DEFAULT ''", []);

    let cat_cnt: i32 = conn.query_row("SELECT COUNT(*) FROM grade_categories", [], |r| r.get(0)).unwrap_or(0);
    if cat_cnt == 0 {
        for (idx, name) in DEFAULT_GRADE_CATEGORIES.iter().enumerate() {
            let _ = conn.execute("INSERT OR IGNORE INTO grade_categories (name, sort_order) VALUES (?1, ?2)", params![*name, idx as i32]);
        }
    }
    Ok(conn)
}

pub fn set_setting(conn: &Connection, key: &str, value: &str) -> Result<(), CoreError> {
    conn.execute("INSERT INTO app_settings (key, value) VALUES (?1, ?2) ON CONFLICT(key) DO UPDATE SET value=excluded.value", params![key, value.trim()]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn get_setting(conn: &Connection, key: &str) -> Result<String, CoreError> {
    match conn.query_row("SELECT value FROM app_settings WHERE key=?1", params![key], |r| r.get::<_, String>(0)) {
        Ok(v) => Ok(v), Err(rusqlite::Error::QueryReturnedNoRows) => Ok(String::new()), Err(e) => Err(CoreError::Database(e.to_string())),
    }
}

pub fn get_classes(conn: &Connection) -> Result<Vec<ClassGroup>, CoreError> {
    let mut stmt = conn.prepare_cached("SELECT MAX(school_name), major, grade, section, COUNT(*) FROM students GROUP BY major, grade, section").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut list: Vec<ClassGroup> = stmt.query_map([], |r| Ok(ClassGroup { school_name: r.get(0)?, major: r.get(1)?, grade: r.get(2)?, section: r.get(3)?, student_count: r.get(4)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    list.sort_by(|a, b| persian_sort_key(&a.major).cmp(&persian_sort_key(&b.major)).then_with(|| grade_rank(&a.grade).cmp(&grade_rank(&b.grade))).then_with(|| a.section.cmp(&b.section)));
    Ok(list)
}

pub fn get_class_attendance(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, period: Period, search_query: &str) -> Result<ClassAttendanceSnapshot, CoreError> {
    let q = normalize_persian(search_query);
    let like = if q.is_empty() { String::new() } else { format!("%{q}%") };
    let pn = period.to_i32();

    let mut stmt = conn.prepare_cached(
        "SELECT s.id, s.row_num, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile,
                COALESCE(MAX(CASE WHEN a.period=1 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period=2 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period=3 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period=4 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period=?5 THEN a.exit_time END), ''),
                COALESCE(MAX(CASE WHEN a.period=?5 THEN a.note END), ''),
                COALESCE((SELECT g.score FROM student_grades g WHERE g.student_id=s.id AND g.score!='' ORDER BY g.updated_at DESC LIMIT 1), '')
         FROM students s LEFT JOIN attendance a ON a.student_id=s.id AND a.date_iso=?4
         WHERE s.major=?1 AND s.grade=?2 AND s.section=?3 AND (?6='' OR s.search_key LIKE ?6)
         GROUP BY s.id",
    ).map_err(|e| CoreError::Database(e.to_string()))?;

    let mut students: Vec<StudentAttendanceRow> = stmt.query_map(params![major, grade, section, date_iso, pn, like], |r| {
        let sts = vec![
            AttendanceStatus::from_i32(r.get(7)?), AttendanceStatus::from_i32(r.get(8)?),
            AttendanceStatus::from_i32(r.get(9)?), AttendanceStatus::from_i32(r.get(10)?),
        ];
        let raw = sts[(pn - 1) as usize];
        let cur = if raw == AttendanceStatus::Unmarked { AttendanceStatus::Present } else { raw };
        Ok(StudentAttendanceRow {
            student_id: r.get(0)?, row_num: r.get(1)?, first_name: r.get(2)?, last_name: r.get(3)?,
            father_name: r.get(4)?, national_id: r.get(5)?, mobile: r.get(6)?,
            current_status: cur, period_statuses: sts, exit_time: r.get(11)?, note: r.get(12)?, latest_grade: r.get(13)?,
        })
    }).map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let saved = students.iter().any(|s| s.period_statuses[(pn - 1) as usize] != AttendanceStatus::Unmarked);
    students.sort_by(|a, b| persian_sort_key(&a.last_name).cmp(&persian_sort_key(&b.last_name)).then_with(|| persian_sort_key(&a.first_name).cmp(&persian_sort_key(&b.first_name))));

    let mut sum = PeriodSummary { total: students.len() as i32, present: 0, absent: 0, late: 0, excused: 0, left_class: 0 };
    for s in &students {
        match s.current_status {
            AttendanceStatus::Absent => sum.absent += 1,
            AttendanceStatus::Late => sum.late += 1,
            AttendanceStatus::Excused => sum.excused += 1,
            AttendanceStatus::LeftClass => sum.left_class += 1,
            _ => sum.present += 1,
        }
    }
    Ok(ClassAttendanceSnapshot { jalali_date: format_iso_to_jalali(date_iso), is_period_saved: saved, summary: sum, students })
}

pub fn set_attendance(conn: &mut Connection, student_id: i64, date_iso: &str, period: Period, status: AttendanceStatus, exit_time: &str, note: &str, teacher: &str, lesson: &str, class_time: &str) -> Result<(), CoreError> {
    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    let now = now_unix();
    let pn = period.to_i32();
    let clean_exit = if status == AttendanceStatus::LeftClass { exit_time.trim() } else { "" };

    tx.execute(
        "INSERT OR IGNORE INTO attendance (student_id, date_iso, period, status, exit_time, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT s2.id, ?2, ?3, 1, '', '', ?4, ?5, ?6, ?7
         FROM students s1 INNER JOIN students s2 ON s2.major=s1.major AND s2.grade=s1.grade AND s2.section=s1.section
         WHERE s1.id=?1",
        params![student_id, date_iso, pn, teacher.trim(), lesson.trim(), class_time.trim(), now],
    ).map_err(|e| CoreError::Database(e.to_string()))?;

    tx.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, exit_time, note, teacher_name, lesson_name, class_time, updated_at)
         VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
             status=excluded.status, exit_time=excluded.exit_time, note=excluded.note,
             teacher_name=excluded.teacher_name, lesson_name=excluded.lesson_name, class_time=excluded.class_time, updated_at=excluded.updated_at",
        params![student_id, date_iso, pn, status.to_i32(), clean_exit, note.trim(), teacher.trim(), lesson.trim(), class_time.trim(), now],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn mark_class_status(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher: &str, lesson: &str, class_time: &str) -> Result<i32, CoreError> {
    let keep = if only_unmarked { 1 } else { 0 };
    let n = conn.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, exit_time, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT id, ?1, ?2, ?3, '', '', ?4, ?5, ?6, ?7 FROM students WHERE major=?8 AND grade=?9 AND section=?10
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
             status = CASE WHEN ?11=1 AND attendance.status!=0 THEN attendance.status ELSE excluded.status END,
             exit_time = CASE WHEN ?11=1 AND attendance.status!=0 THEN attendance.exit_time ELSE '' END,
             note = CASE WHEN ?11=1 AND attendance.status!=0 THEN attendance.note ELSE '' END,
             updated_at=excluded.updated_at",
        params![date_iso, period.to_i32(), status.to_i32(), teacher.trim(), lesson.trim(), class_time.trim(), now_unix(), major, grade, section, keep],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(n as i32)
}

pub fn copy_from_previous_period(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, target: Period) -> Result<i32, CoreError> {
    let prev = target.previous().ok_or_else(|| CoreError::InvalidInput("زنگ اول، زنگ قبلی ندارد".into()))?;
    let n = conn.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, exit_time, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT a.student_id, a.date_iso, ?1, a.status, a.exit_time, a.note, a.teacher_name, a.lesson_name, a.class_time, ?2
         FROM attendance a INNER JOIN students s ON s.id=a.student_id
         WHERE a.date_iso=?3 AND a.period=?4 AND s.major=?5 AND s.grade=?6 AND s.section=?7
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET status=excluded.status, exit_time=excluded.exit_time, note=excluded.note, updated_at=excluded.updated_at",
        params![target.to_i32(), now_unix(), date_iso, prev.to_i32(), major, grade, section],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(n as i32)
}

pub fn add_student(conn: &Connection, school: &str, major: &str, grade: &str, section: i32, f: &str, l: &str, fa: &str, nid_r: &str, mob_r: &str) -> Result<i64, CoreError> {
    let (f, l, nid) = (f.trim(), l.trim(), normalize_national_id(nid_r));
    if f.is_empty() || l.is_empty() { return Err(CoreError::InvalidInput("نام و نام خانوادگی الزامی است".into())); }
    if nid.len() != 10 { return Err(CoreError::InvalidInput("کد ملی باید ۱۰ رقم باشد".into())); }
    let mob = normalize_mobile(mob_r);
    let cm = if is_middle_grade(grade) { "" } else { major.trim() };
    let key = normalize_persian(&format!("{f} {l} {} {nid} {mob}", fa.trim()));
    conn.execute("INSERT INTO students (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, search_key) VALUES (0,?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)",
        params![if school.trim().is_empty() { "آموزشگاه" } else { school.trim() }, cm, grade.trim(), section.max(1), f, l, fa.trim(), nid, mob, key])
        .map_err(|e| if e.to_string().contains("UNIQUE") { CoreError::InvalidInput("کد ملی تکراری است".into()) } else { CoreError::Database(e.to_string()) })?;
    Ok(conn.last_insert_rowid())
}

pub fn update_student(conn: &Connection, id: i64, f: &str, l: &str, fa: &str, nid_r: &str, mob_r: &str) -> Result<(), CoreError> {
    let (f, l, nid) = (f.trim(), l.trim(), normalize_national_id(nid_r));
    if f.is_empty() || l.is_empty() || nid.len() != 10 { return Err(CoreError::InvalidInput("نام، نام خانوادگی و کد ملی ۱۰ رقمی الزامی است".into())); }
    let mob = normalize_mobile(mob_r);
    let key = normalize_persian(&format!("{f} {l} {} {nid} {mob}", fa.trim()));
    conn.execute("UPDATE students SET first_name=?1, last_name=?2, father_name=?3, national_id=?4, mobile=?5, search_key=?6 WHERE id=?7", params![f, l, fa.trim(), nid, mob, key, id])
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn delete_student(conn: &Connection, id: i64) -> Result<(), CoreError> {
    conn.execute("DELETE FROM students WHERE id=?1", params![id]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn delete_class(conn: &Connection, major: &str, grade: &str, section: i32) -> Result<i32, CoreError> {
    let d = conn.execute("DELETE FROM students WHERE major=?1 AND grade=?2 AND section=?3", params![major, grade, section]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(d as i32)
}

// ===== دفتر نمره (مستمر ماهانه / پودمانی / دلخواه) =====
pub fn get_grade_categories(conn: &Connection) -> Result<Vec<GradeCategory>, CoreError> {
    let mut st = conn.prepare_cached("SELECT id, name FROM grade_categories ORDER BY sort_order ASC, id ASC").map_err(|e| CoreError::Database(e.to_string()))?;
    let rows = st.query_map([], |r| Ok(GradeCategory { id: r.get(0)?, name: r.get(1)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(rows)
}

pub fn add_grade_category(conn: &Connection, name: &str) -> Result<i64, CoreError> {
    let n = name.trim();
    if n.is_empty() { return Err(CoreError::InvalidInput("عنوان نمره را وارد کنید".into())); }
    let next_order: i32 = conn.query_row("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM grade_categories", [], |r| r.get(0)).unwrap_or(10);
    conn.execute("INSERT INTO grade_categories (name, sort_order) VALUES (?1, ?2)", params![n, next_order])
        .map_err(|e| if e.to_string().contains("UNIQUE") { CoreError::InvalidInput("این عنوان نمره قبلاً وجود دارد".into()) } else { CoreError::Database(e.to_string()) })?;
    Ok(conn.last_insert_rowid())
}

pub fn delete_grade_category(conn: &Connection, category_id: i64) -> Result<(), CoreError> {
    conn.execute("DELETE FROM grade_categories WHERE id=?1", params![category_id]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn get_class_grades(conn: &Connection, major: &str, grade: &str, section: i32, category_id: i64) -> Result<Vec<StudentGradeRow>, CoreError> {
    let mut st = conn.prepare_cached(
        "SELECT s.id, s.first_name, s.last_name, s.father_name, COALESCE(g.score, ''), COALESCE(g.note, '')
         FROM students s LEFT JOIN student_grades g ON g.student_id=s.id AND g.category_id=?4
         WHERE s.major=?1 AND s.grade=?2 AND s.section=?3",
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    let mut rows: Vec<StudentGradeRow> = st.query_map(params![major, grade, section, category_id], |r| {
        Ok(StudentGradeRow { student_id: r.get(0)?, first_name: r.get(1)?, last_name: r.get(2)?, father_name: r.get(3)?, score: r.get(4)?, note: r.get(5)? })
    }).map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    rows.sort_by(|a, b| persian_sort_key(&a.last_name).cmp(&persian_sort_key(&b.last_name)).then_with(|| persian_sort_key(&a.first_name).cmp(&persian_sort_key(&b.first_name))));
    Ok(rows)
}

pub fn set_student_grade(conn: &Connection, student_id: i64, category_id: i64, score: &str, note: &str) -> Result<(), CoreError> {
    conn.execute(
        "INSERT INTO student_grades (student_id, category_id, score, note, updated_at) VALUES (?1,?2,?3,?4,?5)
         ON CONFLICT(student_id, category_id) DO UPDATE SET score=excluded.score, note=excluded.note, updated_at=excluded.updated_at",
        params![student_id, category_id, score.trim(), note.trim(), now_unix()],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

// ===== مخاطبین ذخیره‌شده (مدیر، معاون، مشاور...) =====
pub fn get_saved_contacts(conn: &Connection) -> Result<Vec<SavedContact>, CoreError> {
    let mut st = conn.prepare_cached("SELECT id, name, role, phone FROM saved_contacts ORDER BY id ASC").map_err(|e| CoreError::Database(e.to_string()))?;
    let rows = st.query_map([], |r| Ok(SavedContact { id: r.get(0)?, name: r.get(1)?, role: r.get(2)?, phone: r.get(3)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(rows)
}

pub fn save_contact(conn: &Connection, name: &str, role: &str, phone: &str) -> Result<i64, CoreError> {
    let p = normalize_mobile(phone);
    if p.is_empty() { return Err(CoreError::InvalidInput("شماره تلفن معتبر وارد کنید".into())); }
    let n = if name.trim().is_empty() { "مخاطب" } else { name.trim() };
    conn.execute("INSERT INTO saved_contacts (name, role, phone) VALUES (?1,?2,?3) ON CONFLICT(phone) DO UPDATE SET name=excluded.name, role=excluded.role", params![n, role.trim(), p])
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(conn.last_insert_rowid())
}

pub fn delete_contact(conn: &Connection, id: i64) -> Result<(), CoreError> {
    conn.execute("DELETE FROM saved_contacts WHERE id=?1", params![id]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

// ===== آمار و گزارش ماهانه =====
pub fn get_backup_stats(conn: &Connection) -> Result<BackupStats, CoreError> {
    Ok(BackupStats {
        students_count: conn.query_row("SELECT COUNT(*) FROM students", [], |r| r.get(0)).unwrap_or(0),
        classes_count: conn.query_row("SELECT COUNT(*) FROM (SELECT DISTINCT major, grade, section FROM students)", [], |r| r.get(0)).unwrap_or(0),
        attendance_count: conn.query_row("SELECT COUNT(*) FROM attendance WHERE status!=0", [], |r| r.get(0)).unwrap_or(0),
        grades_count: conn.query_row("SELECT COUNT(*) FROM student_grades WHERE score!=''", [], |r| r.get(0)).unwrap_or(0),
        contacts_count: conn.query_row("SELECT COUNT(*) FROM saved_contacts", [], |r| r.get(0)).unwrap_or(0),
    })
}

pub fn get_class_analytics(conn: &Connection, major: &str, grade: &str, section: i32) -> Result<ClassAnalytics, CoreError> {
    let mut names = HashMap::new();
    let mut ss = conn.prepare_cached("SELECT id, first_name, last_name FROM students WHERE major=?1 AND grade=?2 AND section=?3").map_err(|e| CoreError::Database(e.to_string()))?;
    for r in ss.query_map(params![major, grade, section], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, String>(2)?))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (id, f, l) = r.map_err(|e| CoreError::Database(e.to_string()))?;
        names.insert(id, format!("{f} {l}"));
    }
    let mut ast = conn.prepare_cached("SELECT a.student_id, a.date_iso, a.period, a.status FROM attendance a INNER JOIN students s ON s.id=a.student_id WHERE s.major=?1 AND s.grade=?2 AND s.section=?3 AND a.status!=0").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut sessions = HashSet::new();
    let (mut ta, mut tl, mut te, mut tlc) = (0, 0, 0, 0);
    let (mut ma, mut ml, mut me, mut mlc): (HashMap<i64, i32>, HashMap<i64, i32>, HashMap<i64, i32>, HashMap<i64, i32>) = Default::default();
    for r in ast.query_map(params![major, grade, section], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?)))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (sid, d, p, st) = r.map_err(|e| CoreError::Database(e.to_string()))?;
        sessions.insert((d, p));
        match st {
            AttendanceStatus::Absent => { ta += 1; *ma.entry(sid).or_default() += 1; }
            AttendanceStatus::Late => { tl += 1; *ml.entry(sid).or_default() += 1; }
            AttendanceStatus::Excused => { te += 1; *me.entry(sid).or_default() += 1; }
            AttendanceStatus::LeftClass => { tlc += 1; *mlc.entry(sid).or_default() += 1; }
            _ => {}
        }
    }
    let rank = |m: HashMap<i64, i32>| -> Vec<TopStudentCount> {
        let mut v: Vec<_> = m.into_iter().filter_map(|(id, c)| names.get(&id).map(|n| TopStudentCount { full_name: n.clone(), count: c })).collect();
        v.sort_by(|a, b| b.count.cmp(&a.count).then_with(|| persian_sort_key(&a.full_name).cmp(&persian_sort_key(&b.full_name))));
        v.truncate(8); v
    };
    Ok(ClassAnalytics { student_count: names.len() as i32, recorded_sessions: sessions.len() as i32, total_absent: ta, total_late: tl, total_excused: te, total_left_class: tlc, top_absent: rank(ma), top_late: rank(ml), top_excused: rank(me), top_left_class: rank(mlc) })
}

pub fn get_monthly_report(conn: &Connection, major: &str, grade: &str, section: i32, jy: i32, jm_i: i32) -> Result<MonthlyClassReport, CoreError> {
    let jm = jm_i.clamp(1, 12) as u32;
    let (s_iso, e_iso) = jalali_month_range_iso(jy, jm);
    let mut ss = conn.prepare_cached("SELECT id, first_name, last_name, father_name, national_id, mobile FROM students WHERE major=?1 AND grade=?2 AND section=?3").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut base: Vec<(i64, String, String, String, String, String)> = ss.query_map(params![major, grade, section], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?, r.get(5)?)))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    base.sort_by(|a, b| persian_sort_key(&a.2).cmp(&persian_sort_key(&b.2)).then_with(|| persian_sort_key(&a.1).cmp(&persian_sort_key(&b.1))));

    let mut ast = conn.prepare_cached("SELECT a.student_id, a.date_iso, a.period, a.status FROM attendance a INNER JOIN students s ON s.id=a.student_id WHERE s.major=?1 AND s.grade=?2 AND s.section=?3 AND a.date_iso>=?4 AND a.date_iso<=?5 AND a.status!=0").map_err(|e| CoreError::Database(e.to_string()))?;
    let (mut active_d, mut stu_d): (HashMap<String, HashSet<i32>>, HashMap<(i64, String), HashMap<i32, AttendanceStatus>>) = Default::default();
    for r in ast.query_map(params![major, grade, section, s_iso, e_iso], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?)))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (sid, d, p, st) = r.map_err(|e| CoreError::Database(e.to_string()))?;
        active_d.entry(d.clone()).or_default().insert(p);
        stu_d.entry((sid, d)).or_default().insert(p, st);
    }

    let (mut tap, mut tfd, mut tlc, mut sp, mut pc) = (0, 0, 0, 0.0f64, 0);
    let mut stats = Vec::with_capacity(base.len());
    for (sid, f, l, fa, nid, mob) in base {
        let (mut pp, mut ap, mut lp, mut ep, mut lcp, mut fad) = (0, 0, 0, 0, 0, 0);
        for (d, act) in &active_d {
            if let Some(dm) = stu_d.get(&(sid, d.clone())) {
                for st in dm.values() {
                    match st {
                        AttendanceStatus::Present => pp += 1, AttendanceStatus::Absent => ap += 1,
                        AttendanceStatus::Late => lp += 1, AttendanceStatus::Excused => ep += 1,
                        AttendanceStatus::LeftClass => lcp += 1, _ => {}
                    }
                }
                if act.len() >= 2 && act.iter().all(|p| matches!(dm.get(p), Some(AttendanceStatus::Absent | AttendanceStatus::Excused))) && act.iter().any(|p| matches!(dm.get(p), Some(AttendanceStatus::Absent))) {
                    fad += 1;
                }
            }
        }
        let tm = pp + ap + lp + ep + lcp;
        let pct = if tm > 0 { let v = ((pp + lp) as f64 / tm as f64) * 100.0; sp += v; pc += 1; (v * 10.0).round() / 10.0 } else { 100.0 };
        tap += ap; tfd += fad; tlc += lcp;
        stats.push(MonthlyStudentStat { student_id: sid, first_name: f, last_name: l, father_name: fa, national_id: nid, mobile: mob, present_periods: pp, absent_periods: ap, full_absent_days: fad, late_periods: lp, excused_periods: ep, left_class_periods: lcp, attendance_percent: pct });
    }
    Ok(MonthlyClassReport {
        jalali_year: jy, jalali_month: jm_i, month_label: format_jalali_month_label(jy, jm),
        recorded_days: active_d.len() as i32,
        average_attendance_percent: if pc > 0 { ((sp / pc as f64) * 10.0).round() / 10.0 } else { 100.0 },
        total_absent_periods: tap, total_full_absent_days: tfd, total_left_class: tlc, students: stats,
    })
}

// ===== پشتیبان کلی JSON (دانش‌آموزان + حضور + خروج + نمرات مستمر/پودمانی + مخاطبین + تنظیمات) =====
#[derive(Serialize, Deserialize)]
struct BkPayload {
    version: i32, students: Vec<BkStu>, attendance: Vec<BkAtt>,
    #[serde(default)] grade_categories: Vec<String>,
    #[serde(default)] grades: Vec<BkGrade>,
    #[serde(default)] contacts: Vec<BkContact>,
    #[serde(default)] settings: HashMap<String, String>,
}
#[derive(Serialize, Deserialize)]
struct BkStu { row_num: i32, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String }
#[derive(Serialize, Deserialize)]
struct BkAtt { national_id: String, date_iso: String, period: i32, status: i32, #[serde(default)] exit_time: String, #[serde(default)] note: String, #[serde(default)] teacher_name: String, #[serde(default)] lesson_name: String, #[serde(default)] class_time: String }
#[derive(Serialize, Deserialize)]
struct BkGrade { national_id: String, category_name: String, score: String, #[serde(default)] note: String }
#[derive(Serialize, Deserialize)]
struct BkContact { name: String, #[serde(default)] role: String, phone: String }

pub fn export_backup_json(conn: &Connection) -> Result<String, CoreError> {
    let students: Vec<BkStu> = conn.prepare("SELECT row_num,school_name,major,grade,section,first_name,last_name,father_name,national_id,mobile FROM students")
        .map_err(|e| CoreError::Database(e.to_string()))?.query_map([], |r| Ok(BkStu { row_num: r.get(0)?, school_name: r.get(1)?, major: r.get(2)?, grade: r.get(3)?, section: r.get(4)?, first_name: r.get(5)?, last_name: r.get(6)?, father_name: r.get(7)?, national_id: r.get(8)?, mobile: r.get(9)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<_, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let attendance: Vec<BkAtt> = conn.prepare("SELECT s.national_id,a.date_iso,a.period,a.status,a.exit_time,a.note,a.teacher_name,a.lesson_name,a.class_time FROM attendance a INNER JOIN students s ON s.id=a.student_id")
        .map_err(|e| CoreError::Database(e.to_string()))?.query_map([], |r| Ok(BkAtt { national_id: r.get(0)?, date_iso: r.get(1)?, period: r.get(2)?, status: r.get(3)?, exit_time: r.get(4)?, note: r.get(5)?, teacher_name: r.get(6)?, lesson_name: r.get(7)?, class_time: r.get(8)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<_, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let grade_categories: Vec<String> = conn.prepare("SELECT name FROM grade_categories ORDER BY sort_order ASC, id ASC")
        .map_err(|e| CoreError::Database(e.to_string()))?.query_map([], |r| r.get(0)).map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<_, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let grades: Vec<BkGrade> = conn.prepare("SELECT s.national_id,c.name,g.score,g.note FROM student_grades g INNER JOIN students s ON s.id=g.student_id INNER JOIN grade_categories c ON c.id=g.category_id WHERE g.score!='' OR g.note!=''")
        .map_err(|e| CoreError::Database(e.to_string()))?.query_map([], |r| Ok(BkGrade { national_id: r.get(0)?, category_name: r.get(1)?, score: r.get(2)?, note: r.get(3)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<_, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let contacts: Vec<BkContact> = conn.prepare("SELECT name,role,phone FROM saved_contacts")
        .map_err(|e| CoreError::Database(e.to_string()))?.query_map([], |r| Ok(BkContact { name: r.get(0)?, role: r.get(1)?, phone: r.get(2)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<_, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut settings = HashMap::new();
    for r in conn.prepare("SELECT key,value FROM app_settings").map_err(|e| CoreError::Database(e.to_string()))?.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (k, v) = r.map_err(|e| CoreError::Database(e.to_string()))?;
        settings.insert(k, v);
    }
    serde_json::to_string_pretty(&BkPayload { version: 4, students, attendance, grade_categories, grades, contacts, settings }).map_err(|e| CoreError::Import(e.to_string()))
}

pub fn restore_backup_json(conn: &mut Connection, json_text: &str) -> Result<ImportReport, CoreError> {
    let p: BkPayload = serde_json::from_str(json_text.trim_start_matches('\u{FEFF}')).map_err(|e| CoreError::Import(format!("فایل پشتیبان معتبر نیست: {e}")))?;
    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    tx.execute_batch("DELETE FROM student_grades; DELETE FROM attendance; DELETE FROM students; DELETE FROM saved_contacts;").map_err(|e| CoreError::Database(e.to_string()))?;

    let mut stu_map = HashMap::new();
    for s in &p.students {
        let key = normalize_persian(&format!("{} {} {} {} {}", s.first_name, s.last_name, s.father_name, s.national_id, s.mobile));
        tx.execute("INSERT INTO students (row_num,school_name,major,grade,section,first_name,last_name,father_name,national_id,mobile,search_key) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)",
            params![s.row_num, s.school_name, s.major, s.grade, s.section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, key]).map_err(|e| CoreError::Database(e.to_string()))?;
        stu_map.insert(s.national_id.clone(), tx.last_insert_rowid());
    }
    let now = now_unix();
    for a in &p.attendance {
        if let Some(&sid) = stu_map.get(&a.national_id) {
            let _ = tx.execute("INSERT OR REPLACE INTO attendance (student_id,date_iso,period,status,exit_time,note,teacher_name,lesson_name,class_time,updated_at) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)",
                params![sid, a.date_iso, a.period, a.status, a.exit_time, a.note, a.teacher_name, a.lesson_name, a.class_time, now]);
        }
    }
    for (i, cname) in p.grade_categories.iter().enumerate() {
        let _ = tx.execute("INSERT OR IGNORE INTO grade_categories (name, sort_order) VALUES (?1,?2)", params![cname, i as i32]);
    }
    let mut cat_map = HashMap::new();
    {
        let mut cst = tx.prepare("SELECT id, name FROM grade_categories").map_err(|e| CoreError::Database(e.to_string()))?;
        for r in cst.query_map([], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?))).map_err(|e| CoreError::Database(e.to_string()))? {
            if let Ok((id, n)) = r { cat_map.insert(n, id); }
        }
    }
    for g in &p.grades {
        if let (Some(&sid), Some(&cid)) = (stu_map.get(&g.national_id), cat_map.get(&g.category_name)) {
            let _ = tx.execute("INSERT OR REPLACE INTO student_grades (student_id,category_id,score,note,updated_at) VALUES (?1,?2,?3,?4,?5)", params![sid, cid, g.score, g.note, now]);
        }
    }
    for c in &p.contacts {
        let _ = tx.execute("INSERT OR IGNORE INTO saved_contacts (name,role,phone) VALUES (?1,?2,?3)", params![c.name, c.role, c.phone]);
    }
    for (k, v) in &p.settings {
        let _ = tx.execute("INSERT INTO app_settings (key,value) VALUES (?1,?2) ON CONFLICT(key) DO UPDATE SET value=excluded.value", params![k, v]);
    }
    let classes: i32 = tx.query_row("SELECT COUNT(*) FROM (SELECT DISTINCT major,grade,section FROM students)", [], |r| r.get(0)).unwrap_or(0);
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(ImportReport { imported_count: p.students.len() as i32, skipped_count: 0, classes_count: classes })
}

fn now_unix() -> i64 { SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0) }
