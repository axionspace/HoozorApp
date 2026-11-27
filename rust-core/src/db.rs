use crate::models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    ImportReport, MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary,
    StudentAttendanceRow, TopStudentCount,
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

pub fn init_database(db_path: &str) -> Result<Connection, CoreError> {
    let conn = if db_path == ":memory:" { Connection::open_in_memory() } else { Connection::open(db_path) }
        .map_err(|e| CoreError::Database(e.to_string()))?;

    conn.execute_batch(
        "PRAGMA journal_mode = WAL;
         PRAGMA synchronous = NORMAL;
         PRAGMA foreign_keys = ON;
         PRAGMA temp_store = MEMORY;
         PRAGMA cache_size = -4000;

         CREATE TABLE IF NOT EXISTS students (
             id          INTEGER PRIMARY KEY AUTOINCREMENT,
             row_num     INTEGER NOT NULL,
             school_name TEXT NOT NULL,
             major       TEXT NOT NULL,
             grade       TEXT NOT NULL,
             section     INTEGER NOT NULL,
             first_name  TEXT NOT NULL,
             last_name   TEXT NOT NULL,
             father_name TEXT NOT NULL,
             national_id TEXT NOT NULL UNIQUE,
             mobile      TEXT NOT NULL,
             class_score TEXT NOT NULL DEFAULT '',
             search_key  TEXT NOT NULL
         );

         CREATE TABLE IF NOT EXISTS attendance (
             student_id   INTEGER NOT NULL,
             date_iso     TEXT NOT NULL,
             period       INTEGER NOT NULL CHECK(period BETWEEN 1 AND 4),
             status       INTEGER NOT NULL,
             score        TEXT NOT NULL DEFAULT '',
             note         TEXT NOT NULL DEFAULT '',
             teacher_name TEXT NOT NULL DEFAULT '',
             lesson_name  TEXT NOT NULL DEFAULT '',
             class_time   TEXT NOT NULL DEFAULT '',
             updated_at   INTEGER NOT NULL,
             PRIMARY KEY (student_id, date_iso, period),
             FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
         );

         CREATE TABLE IF NOT EXISTS app_settings (
             key   TEXT PRIMARY KEY,
             value TEXT NOT NULL
         );

         CREATE INDEX IF NOT EXISTS idx_students_class ON students(major, grade, section);
         CREATE INDEX IF NOT EXISTS idx_students_search ON students(search_key);
         CREATE INDEX IF NOT EXISTS idx_attendance_date_period ON attendance(date_iso, period, student_id);",
    )
    .map_err(|e| CoreError::Database(e.to_string()))?;

    let _ = conn.execute("ALTER TABLE students ADD COLUMN class_score TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN score TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN teacher_name TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN lesson_name TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN class_time TEXT NOT NULL DEFAULT ''", []);
    Ok(conn)
}

pub fn set_setting(conn: &Connection, key: &str, value: &str) -> Result<(), CoreError> {
    conn.execute(
        "INSERT INTO app_settings (key, value) VALUES (?1, ?2) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        params![key, value.trim()],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn get_setting(conn: &Connection, key: &str) -> Result<String, CoreError> {
    match conn.query_row("SELECT value FROM app_settings WHERE key = ?1", params![key], |r| r.get::<_, String>(0)) {
        Ok(v) => Ok(v),
        Err(rusqlite::Error::QueryReturnedNoRows) => Ok(String::new()),
        Err(e) => Err(CoreError::Database(e.to_string())),
    }
}

pub fn get_classes(conn: &Connection) -> Result<Vec<ClassGroup>, CoreError> {
    let mut stmt = conn
        .prepare_cached("SELECT MAX(school_name), major, grade, section, COUNT(*) FROM students GROUP BY major, grade, section")
        .map_err(|e| CoreError::Database(e.to_string()))?;
    let mut classes: Vec<ClassGroup> = stmt
        .query_map([], |r| Ok(ClassGroup { school_name: r.get(0)?, major: r.get(1)?, grade: r.get(2)?, section: r.get(3)?, student_count: r.get(4)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    classes.sort_by(|a, b| {
        persian_sort_key(&a.major).cmp(&persian_sort_key(&b.major))
            .then_with(|| grade_rank(&a.grade).cmp(&grade_rank(&b.grade)))
            .then_with(|| a.section.cmp(&b.section))
    });
    Ok(classes)
}

pub fn get_class_attendance(
    conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, period: Period, search_query: &str,
) -> Result<ClassAttendanceSnapshot, CoreError> {
    let norm_q = normalize_persian(search_query);
    let like_pat = if norm_q.is_empty() { String::new() } else { format!("%{norm_q}%") };
    let p_num = period.to_i32();

    let mut stmt = conn.prepare_cached(
        "SELECT s.id, s.row_num, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, s.class_score,
                COALESCE(MAX(CASE WHEN a.period = 1 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period = 2 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period = 3 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period = 4 THEN a.status END), 0),
                COALESCE(MAX(CASE WHEN a.period = ?5 THEN a.score END), ''),
                COALESCE(MAX(CASE WHEN a.period = ?5 THEN a.note END), '')
         FROM students s
         LEFT JOIN attendance a ON a.student_id = s.id AND a.date_iso = ?4
         WHERE s.major = ?1 AND s.grade = ?2 AND s.section = ?3 AND (?6 = '' OR s.search_key LIKE ?6)
         GROUP BY s.id",
    ).map_err(|e| CoreError::Database(e.to_string()))?;

    let mut students: Vec<StudentAttendanceRow> = stmt
        .query_map(params![major, grade, section, date_iso, p_num, like_pat], |r| {
            let statuses = vec![
                AttendanceStatus::from_i32(r.get(8)?),
                AttendanceStatus::from_i32(r.get(9)?),
                AttendanceStatus::from_i32(r.get(10)?),
                AttendanceStatus::from_i32(r.get(11)?),
            ];
            let raw_cur = statuses[(p_num - 1) as usize];
            let current_status = if raw_cur == AttendanceStatus::Unmarked { AttendanceStatus::Present } else { raw_cur };
            Ok(StudentAttendanceRow {
                student_id: r.get(0)?, row_num: r.get(1)?, first_name: r.get(2)?, last_name: r.get(3)?,
                father_name: r.get(4)?, national_id: r.get(5)?, mobile: r.get(6)?, class_score: r.get(7)?,
                current_status, period_statuses: statuses, session_score: r.get(12)?, note: r.get(13)?,
            })
        })
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let is_period_saved = students.iter().any(|s| s.period_statuses[(p_num - 1) as usize] != AttendanceStatus::Unmarked);
    students.sort_by(|a, b| persian_sort_key(&a.last_name).cmp(&persian_sort_key(&b.last_name)).then_with(|| persian_sort_key(&a.first_name).cmp(&persian_sort_key(&b.first_name))));

    let mut summary = PeriodSummary { total: students.len() as i32, present: 0, absent: 0, late: 0, excused: 0, unmarked: 0 };
    for s in &students {
        match s.current_status {
            AttendanceStatus::Present => summary.present += 1,
            AttendanceStatus::Absent => summary.absent += 1,
            AttendanceStatus::Late => summary.late += 1,
            AttendanceStatus::Excused => summary.excused += 1,
            AttendanceStatus::Unmarked => summary.unmarked += 1,
        }
    }
    Ok(ClassAttendanceSnapshot { jalali_date: format_iso_to_jalali(date_iso), is_period_saved, summary, students })
}

pub fn set_attendance(
    conn: &mut Connection, student_id: i64, date_iso: &str, period: Period, status: AttendanceStatus,
    note: &str, teacher_name: &str, lesson_name: &str, class_time: &str,
) -> Result<(), CoreError> {
    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    let now = now_unix();
    let p_num = period.to_i32();

    tx.execute(
        "INSERT OR IGNORE INTO attendance (student_id, date_iso, period, status, score, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT s2.id, ?2, ?3, 1, '', '', ?4, ?5, ?6, ?7
         FROM students s1 INNER JOIN students s2 ON s2.major = s1.major AND s2.grade = s1.grade AND s2.section = s1.section
         WHERE s1.id = ?1",
        params![student_id, date_iso, p_num, teacher_name.trim(), lesson_name.trim(), class_time.trim(), now],
    ).map_err(|e| CoreError::Database(e.to_string()))?;

    tx.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, score, note, teacher_name, lesson_name, class_time, updated_at)
         VALUES (?1, ?2, ?3, ?4, '', ?5, ?6, ?7, ?8, ?9)
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
             status = excluded.status, note = excluded.note, teacher_name = excluded.teacher_name,
             lesson_name = excluded.lesson_name, class_time = excluded.class_time, updated_at = excluded.updated_at",
        params![student_id, date_iso, p_num, status.to_i32(), note.trim(), teacher_name.trim(), lesson_name.trim(), class_time.trim(), now],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn set_student_score(conn: &Connection, student_id: i64, date_iso: &str, period: Period, class_score: &str, session_score: &str) -> Result<(), CoreError> {
    conn.execute("UPDATE students SET class_score = ?1 WHERE id = ?2", params![class_score.trim(), student_id])
        .map_err(|e| CoreError::Database(e.to_string()))?;
    if !session_score.trim().is_empty() {
        conn.execute(
            "INSERT INTO attendance (student_id, date_iso, period, status, score, note, teacher_name, lesson_name, class_time, updated_at)
             VALUES (?1, ?2, ?3, 1, ?4, '', '', '', '', ?5)
             ON CONFLICT(student_id, date_iso, period) DO UPDATE SET score = excluded.score, updated_at = excluded.updated_at",
            params![student_id, date_iso, period.to_i32(), session_score.trim(), now_unix()],
        ).map_err(|e| CoreError::Database(e.to_string()))?;
    }
    Ok(())
}

pub fn mark_class_status(
    conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, period: Period,
    status: AttendanceStatus, only_unmarked: bool, teacher_name: &str, lesson_name: &str, class_time: &str,
) -> Result<i32, CoreError> {
    let keep = if only_unmarked { 1 } else { 0 };
    let changed = conn.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, score, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT id, ?1, ?2, ?3, '', '', ?4, ?5, ?6, ?7 FROM students WHERE major = ?8 AND grade = ?9 AND section = ?10
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
             status = CASE WHEN ?11 = 1 AND attendance.status != 0 THEN attendance.status ELSE excluded.status END,
             teacher_name = excluded.teacher_name, lesson_name = excluded.lesson_name, class_time = excluded.class_time, updated_at = excluded.updated_at",
        params![date_iso, period.to_i32(), status.to_i32(), teacher_name.trim(), lesson_name.trim(), class_time.trim(), now_unix(), major, grade, section, keep],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(changed as i32)
}

pub fn copy_from_previous_period(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, target_period: Period) -> Result<i32, CoreError> {
    let prev = target_period.previous().ok_or_else(|| CoreError::InvalidInput("زنگ اول، زنگ قبلی ندارد".into()))?;
    let copied = conn.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, score, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT a.student_id, a.date_iso, ?1, a.status, a.score, a.note, a.teacher_name, a.lesson_name, a.class_time, ?2
         FROM attendance a INNER JOIN students s ON s.id = a.student_id
         WHERE a.date_iso = ?3 AND a.period = ?4 AND s.major = ?5 AND s.grade = ?6 AND s.section = ?7
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET status = excluded.status, note = excluded.note, updated_at = excluded.updated_at",
        params![target_period.to_i32(), now_unix(), date_iso, prev.to_i32(), major, grade, section],
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(copied as i32)
}

pub fn add_student(conn: &Connection, school_name: &str, major: &str, grade: &str, section: i32, first: &str, last: &str, father: &str, nid_raw: &str, mobile_raw: &str, score: &str) -> Result<i64, CoreError> {
    let (f, l, nid) = (first.trim(), last.trim(), normalize_national_id(nid_raw));
    if f.is_empty() || l.is_empty() { return Err(CoreError::InvalidInput("نام و نام خانوادگی الزامی است".into())); }
    if nid.len() != 10 { return Err(CoreError::InvalidInput("کد ملی باید ۱۰ رقم باشد".into())); }
    let school = if school_name.trim().is_empty() { "آموزشگاه" } else { school_name.trim() };
    let clean_major = if is_middle_grade(grade) { "" } else { major.trim() };
    let mob = normalize_mobile(mobile_raw);
    let key = normalize_persian(&format!("{f} {l} {} {nid} {mob}", father.trim()));
    conn.execute(
        "INSERT INTO students (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, class_score, search_key)
         VALUES (0, ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)",
        params![school, clean_major, grade.trim(), section.max(1), f, l, father.trim(), nid, mob, score.trim(), key],
    ).map_err(|e| if e.to_string().contains("UNIQUE") { CoreError::InvalidInput("این کد ملی قبلاً ثبت شده است".into()) } else { CoreError::Database(e.to_string()) })?;
    Ok(conn.last_insert_rowid())
}

pub fn update_student(conn: &Connection, student_id: i64, first: &str, last: &str, father: &str, nid_raw: &str, mobile_raw: &str, score: &str) -> Result<(), CoreError> {
    let (f, l, nid) = (first.trim(), last.trim(), normalize_national_id(nid_raw));
    if f.is_empty() || l.is_empty() { return Err(CoreError::InvalidInput("نام و نام خانوادگی الزامی است".into())); }
    if nid.len() != 10 { return Err(CoreError::InvalidInput("کد ملی باید ۱۰ رقم باشد".into())); }
    let mob = normalize_mobile(mobile_raw);
    let key = normalize_persian(&format!("{f} {l} {} {nid} {mob}", father.trim()));
    conn.execute(
        "UPDATE students SET first_name = ?1, last_name = ?2, father_name = ?3, national_id = ?4, mobile = ?5, class_score = ?6, search_key = ?7 WHERE id = ?8",
        params![f, l, father.trim(), nid, mob, score.trim(), key, student_id],
    ).map_err(|e| if e.to_string().contains("UNIQUE") { CoreError::InvalidInput("این کد ملی متعلق به دانش‌آموز دیگری است".into()) } else { CoreError::Database(e.to_string()) })?;
    Ok(())
}

pub fn delete_student(conn: &Connection, student_id: i64) -> Result<(), CoreError> {
    conn.execute("DELETE FROM students WHERE id = ?1", params![student_id]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn delete_class(conn: &Connection, major: &str, grade: &str, section: i32) -> Result<i32, CoreError> {
    let d = conn.execute("DELETE FROM students WHERE major = ?1 AND grade = ?2 AND section = ?3", params![major, grade, section]).map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(d as i32)
}

pub fn get_backup_stats(conn: &Connection) -> Result<BackupStats, CoreError> {
    let students_count: i32 = conn.query_row("SELECT COUNT(*) FROM students", [], |r| r.get(0)).unwrap_or(0);
    let classes_count: i32 = conn.query_row("SELECT COUNT(*) FROM (SELECT DISTINCT major, grade, section FROM students)", [], |r| r.get(0)).unwrap_or(0);
    let attendance_count: i32 = conn.query_row("SELECT COUNT(*) FROM attendance WHERE status != 0", [], |r| r.get(0)).unwrap_or(0);
    let scores_count: i32 = conn.query_row("SELECT (SELECT COUNT(*) FROM students WHERE class_score != '') + (SELECT COUNT(*) FROM attendance WHERE score != '')", [], |r| r.get(0)).unwrap_or(0);
    Ok(BackupStats { students_count, classes_count, attendance_count, scores_count })
}

pub fn get_class_analytics(conn: &Connection, major: &str, grade: &str, section: i32) -> Result<ClassAnalytics, CoreError> {
    let mut names = HashMap::new();
    let mut s_stmt = conn.prepare_cached("SELECT id, first_name, last_name FROM students WHERE major = ?1 AND grade = ?2 AND section = ?3").map_err(|e| CoreError::Database(e.to_string()))?;
    for row in s_stmt.query_map(params![major, grade, section], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, String>(2)?))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (id, f, l) = row.map_err(|e| CoreError::Database(e.to_string()))?;
        names.insert(id, format!("{f} {l}"));
    }

    let mut a_stmt = conn.prepare_cached(
        "SELECT a.student_id, a.date_iso, a.period, a.status FROM attendance a INNER JOIN students s ON s.id = a.student_id
         WHERE s.major = ?1 AND s.grade = ?2 AND s.section = ?3 AND a.status != 0",
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    let mut sessions = HashSet::new();
    let (mut total_absent, mut total_late, mut total_excused) = (0, 0, 0);
    let (mut abs_m, mut late_m, mut exc_m): (HashMap<i64, i32>, HashMap<i64, i32>, HashMap<i64, i32>) = (HashMap::new(), HashMap::new(), HashMap::new());
    for row in a_stmt.query_map(params![major, grade, section], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?)))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (sid, date, period, st) = row.map_err(|e| CoreError::Database(e.to_string()))?;
        sessions.insert((date, period));
        match st {
            AttendanceStatus::Absent => { total_absent += 1; *abs_m.entry(sid).or_default() += 1; }
            AttendanceStatus::Late => { total_late += 1; *late_m.entry(sid).or_default() += 1; }
            AttendanceStatus::Excused => { total_excused += 1; *exc_m.entry(sid).or_default() += 1; }
            _ => {}
        }
    }
    let rank = |m: HashMap<i64, i32>| -> Vec<TopStudentCount> {
        let mut v: Vec<_> = m.into_iter().filter_map(|(sid, count)| names.get(&sid).map(|n| TopStudentCount { full_name: n.clone(), count })).collect();
        v.sort_by(|a, b| b.count.cmp(&a.count).then_with(|| persian_sort_key(&a.full_name).cmp(&persian_sort_key(&b.full_name))));
        v.truncate(8);
        v
    };
    Ok(ClassAnalytics { student_count: names.len() as i32, recorded_sessions: sessions.len() as i32, total_absent, total_late, total_excused, top_absent: rank(abs_m), top_late: rank(late_m), top_excused: rank(exc_m) })
}

pub fn get_monthly_report(conn: &Connection, major: &str, grade: &str, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
    let jm = jalali_month.clamp(1, 12) as u32;
    let (start_iso, end_iso) = jalali_month_range_iso(jalali_year, jm);

    let mut s_stmt = conn.prepare_cached("SELECT id, first_name, last_name, father_name, national_id, mobile, class_score FROM students WHERE major = ?1 AND grade = ?2 AND section = ?3").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut base: Vec<(i64, String, String, String, String, String, String)> = s_stmt
        .query_map(params![major, grade, section], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?, r.get(5)?, r.get(6)?)))
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;
    base.sort_by(|a, b| persian_sort_key(&a.2).cmp(&persian_sort_key(&b.2)).then_with(|| persian_sort_key(&a.1).cmp(&persian_sort_key(&b.1))));

    let mut a_stmt = conn.prepare_cached(
        "SELECT a.student_id, a.date_iso, a.period, a.status FROM attendance a INNER JOIN students s ON s.id = a.student_id
         WHERE s.major = ?1 AND s.grade = ?2 AND s.section = ?3 AND a.date_iso >= ?4 AND a.date_iso <= ?5 AND a.status != 0",
    ).map_err(|e| CoreError::Database(e.to_string()))?;
    let mut active_by_date: HashMap<String, HashSet<i32>> = HashMap::new();
    let mut stu_days: HashMap<(i64, String), HashMap<i32, AttendanceStatus>> = HashMap::new();
    for row in a_stmt.query_map(params![major, grade, section, start_iso, end_iso], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?)))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (sid, date, p, st) = row.map_err(|e| CoreError::Database(e.to_string()))?;
        active_by_date.entry(date.clone()).or_default().insert(p);
        stu_days.entry((sid, date)).or_default().insert(p, st);
    }

    let recorded_days = active_by_date.len() as i32;
    let (mut total_abs_p, mut total_full_d, mut sum_pct, mut pct_cnt) = (0, 0, 0.0f64, 0);
    let mut stats = Vec::with_capacity(base.len());
    for (sid, first, last, father, nid, mob, class_score) in base {
        let (mut pp, mut ap, mut lp, mut ep, mut fad) = (0, 0, 0, 0, 0);
        for (date, act_p) in &active_by_date {
            if let Some(dm) = stu_days.get(&(sid, date.clone())) {
                for st in dm.values() {
                    match st {
                        AttendanceStatus::Present => pp += 1,
                        AttendanceStatus::Absent => ap += 1,
                        AttendanceStatus::Late => lp += 1,
                        AttendanceStatus::Excused => ep += 1,
                        AttendanceStatus::Unmarked => {}
                    }
                }
                if act_p.len() >= 2 && act_p.iter().all(|p| matches!(dm.get(p), Some(AttendanceStatus::Absent | AttendanceStatus::Excused))) && act_p.iter().any(|p| matches!(dm.get(p), Some(AttendanceStatus::Absent))) {
                    fad += 1;
                }
            }
        }
        let tm = pp + ap + lp + ep;
        let pct = if tm > 0 { let v = ((pp + lp) as f64 / tm as f64) * 100.0; sum_pct += v; pct_cnt += 1; (v * 10.0).round() / 10.0 } else { 100.0 };
        total_abs_p += ap;
        total_full_d += fad;
        stats.push(MonthlyStudentStat { student_id: sid, first_name: first, last_name: last, father_name: father, national_id: nid, mobile: mob, class_score, present_periods: pp, absent_periods: ap, full_absent_days: fad, late_periods: lp, excused_periods: ep, attendance_percent: pct });
    }
    let avg = if pct_cnt > 0 { ((sum_pct / pct_cnt as f64) * 10.0).round() / 10.0 } else { 100.0 };
    Ok(MonthlyClassReport { jalali_year, jalali_month, month_label: format_jalali_month_label(jalali_year, jm), recorded_days, average_attendance_percent: avg, total_absent_periods: total_abs_p, total_full_absent_days: total_full_d, students: stats })
}

#[derive(Serialize, Deserialize)]
struct BackupPayload {
    version: i32,
    students: Vec<BackupStudent>,
    attendance: Vec<BackupAttendance>,
    #[serde(default)]
    settings: HashMap<String, String>,
}

#[derive(Serialize, Deserialize)]
struct BackupStudent {
    row_num: i32, school_name: String, major: String, grade: String, section: i32,
    first_name: String, last_name: String, father_name: String, national_id: String, mobile: String,
    #[serde(default)]
    class_score: String,
}

#[derive(Serialize, Deserialize)]
struct BackupAttendance {
    national_id: String, date_iso: String, period: i32, status: i32,
    #[serde(default)]
    score: String,
    #[serde(default)]
    note: String,
    #[serde(default)]
    teacher_name: String,
    #[serde(default)]
    lesson_name: String,
    #[serde(default)]
    class_time: String,
}

pub fn export_backup_json(conn: &Connection) -> Result<String, CoreError> {
    let mut s_stmt = conn.prepare("SELECT row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, class_score FROM students").map_err(|e| CoreError::Database(e.to_string()))?;
    let students: Vec<BackupStudent> = s_stmt
        .query_map([], |r| Ok(BackupStudent { row_num: r.get(0)?, school_name: r.get(1)?, major: r.get(2)?, grade: r.get(3)?, section: r.get(4)?, first_name: r.get(5)?, last_name: r.get(6)?, father_name: r.get(7)?, national_id: r.get(8)?, mobile: r.get(9)?, class_score: r.get(10)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut a_stmt = conn.prepare("SELECT s.national_id, a.date_iso, a.period, a.status, a.score, a.note, a.teacher_name, a.lesson_name, a.class_time FROM attendance a INNER JOIN students s ON s.id = a.student_id").map_err(|e| CoreError::Database(e.to_string()))?;
    let attendance: Vec<BackupAttendance> = a_stmt
        .query_map([], |r| Ok(BackupAttendance { national_id: r.get(0)?, date_iso: r.get(1)?, period: r.get(2)?, status: r.get(3)?, score: r.get(4)?, note: r.get(5)?, teacher_name: r.get(6)?, lesson_name: r.get(7)?, class_time: r.get(8)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut set_stmt = conn.prepare("SELECT key, value FROM app_settings").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut settings = HashMap::new();
    for r in set_stmt.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (k, v) = r.map_err(|e| CoreError::Database(e.to_string()))?;
        settings.insert(k, v);
    }
    serde_json::to_string_pretty(&BackupPayload { version: 3, students, attendance, settings }).map_err(|e| CoreError::Import(e.to_string()))
}

pub fn restore_backup_json(conn: &mut Connection, json_text: &str) -> Result<ImportReport, CoreError> {
    let payload: BackupPayload = serde_json::from_str(json_text.trim_start_matches('\u{FEFF}'))
        .map_err(|e| CoreError::Import(format!("فایل پشتیبان JSON معتبر نیست: {e}")))?;
    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    tx.execute("DELETE FROM attendance", []).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.execute("DELETE FROM students", []).map_err(|e| CoreError::Database(e.to_string()))?;

    let mut id_map = HashMap::new();
    {
        let mut stmt = tx.prepare_cached("INSERT INTO students (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, class_score, search_key) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)").map_err(|e| CoreError::Database(e.to_string()))?;
        for s in &payload.students {
            let key = normalize_persian(&format!("{} {} {} {} {}", s.first_name, s.last_name, s.father_name, s.national_id, s.mobile));
            stmt.execute(params![s.row_num, s.school_name, s.major, s.grade, s.section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, s.class_score, key]).map_err(|e| CoreError::Database(e.to_string()))?;
            id_map.insert(s.national_id.clone(), tx.last_insert_rowid());
        }
    }
    {
        let mut a_stmt = tx.prepare_cached("INSERT OR REPLACE INTO attendance (student_id, date_iso, period, status, score, note, teacher_name, lesson_name, class_time, updated_at) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)").map_err(|e| CoreError::Database(e.to_string()))?;
        let now = now_unix();
        for a in &payload.attendance {
            if let Some(&sid) = id_map.get(&a.national_id) {
                let _ = a_stmt.execute(params![sid, a.date_iso, a.period, a.status, a.score, a.note, a.teacher_name, a.lesson_name, a.class_time, now]);
            }
        }
    }
    for (k, v) in &payload.settings {
        let _ = tx.execute("INSERT INTO app_settings (key, value) VALUES (?1, ?2) ON CONFLICT(key) DO UPDATE SET value = excluded.value", params![k, v]);
    }
    let classes_count: i32 = tx.query_row("SELECT COUNT(*) FROM (SELECT DISTINCT major, grade, section FROM students)", [], |r| r.get(0)).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(ImportReport { imported_count: payload.students.len() as i32, skipped_count: 0, classes_count })
}

fn now_unix() -> i64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0)
}
