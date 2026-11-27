use crate::models::{
    AttendanceStatus, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError, ImportReport,
    MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary, StudentAttendanceRow,
    TopStudentCount,
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
    let conn = if db_path == ":memory:" {
        Connection::open_in_memory()
    } else {
        Connection::open(db_path)
    }
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
             national_id TEXT NOT NULL,
             mobile      TEXT NOT NULL,
             search_key  TEXT NOT NULL,
             UNIQUE(school_name, national_id)
         );

         CREATE TABLE IF NOT EXISTS attendance (
             student_id   INTEGER NOT NULL,
             date_iso     TEXT NOT NULL,
             period       INTEGER NOT NULL CHECK(period BETWEEN 1 AND 4),
             status       INTEGER NOT NULL,
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

         CREATE INDEX IF NOT EXISTS idx_students_class ON students(school_name, major, grade, section);
         CREATE INDEX IF NOT EXISTS idx_students_search ON students(search_key);
         CREATE INDEX IF NOT EXISTS idx_attendance_date_period ON attendance(date_iso, period, student_id);",
    )
    .map_err(|e| CoreError::Database(e.to_string()))?;

    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN teacher_name TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN lesson_name TEXT NOT NULL DEFAULT ''", []);
    let _ = conn.execute("ALTER TABLE attendance ADD COLUMN class_time TEXT NOT NULL DEFAULT ''", []);

    Ok(conn)
}

pub fn set_setting(conn: &Connection, key: &str, value: &str) -> Result<(), CoreError> {
    conn.execute(
        "INSERT INTO app_settings (key, value) VALUES (?1, ?2)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        params![key, value.trim()],
    )
    .map_err(|e| CoreError::Database(e.to_string()))?;
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
        .prepare_cached("SELECT school_name, major, grade, section, COUNT(*) FROM students GROUP BY school_name, major, grade, section")
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut classes: Vec<ClassGroup> = stmt
        .query_map([], |row| {
            Ok(ClassGroup {
                school_name: row.get(0)?,
                major: row.get(1)?,
                grade: row.get(2)?,
                section: row.get(3)?,
                student_count: row.get(4)?,
            })
        })
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    classes.sort_by(|a, b| {
        persian_sort_key(&a.school_name)
            .cmp(&persian_sort_key(&b.school_name))
            .then_with(|| persian_sort_key(&a.major).cmp(&persian_sort_key(&b.major)))
            .then_with(|| grade_rank(&a.grade).cmp(&grade_rank(&b.grade)))
            .then_with(|| a.section.cmp(&b.section))
    });
    Ok(classes)
}

pub fn get_class_attendance(
    conn: &Connection,
    school_name: &str,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
    period: Period,
    search_query: &str,
) -> Result<ClassAttendanceSnapshot, CoreError> {
    let norm_query = normalize_persian(search_query);
    let like_pattern = if norm_query.is_empty() { String::new() } else { format!("%{norm_query}%") };
    let period_num = period.to_i32();

    let mut stmt = conn
        .prepare_cached(
            "SELECT
                 s.id, s.row_num, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile,
                 COALESCE(MAX(CASE WHEN a.period = 1 THEN a.status END), 0) AS p1,
                 COALESCE(MAX(CASE WHEN a.period = 2 THEN a.status END), 0) AS p2,
                 COALESCE(MAX(CASE WHEN a.period = 3 THEN a.status END), 0) AS p3,
                 COALESCE(MAX(CASE WHEN a.period = 4 THEN a.status END), 0) AS p4,
                 COALESCE(MAX(CASE WHEN a.period = ?6 THEN a.note END), '') AS cur_note
             FROM students s
             LEFT JOIN attendance a ON a.student_id = s.id AND a.date_iso = ?5
             WHERE s.school_name = ?1 AND s.major = ?2 AND s.grade = ?3 AND s.section = ?4
               AND (?7 = '' OR s.search_key LIKE ?7)
             GROUP BY s.id",
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut students: Vec<StudentAttendanceRow> = stmt
        .query_map(params![school_name, major, grade, section, date_iso, period_num, like_pattern], |row| {
            let statuses = vec![
                AttendanceStatus::from_i32(row.get(7)?),
                AttendanceStatus::from_i32(row.get(8)?),
                AttendanceStatus::from_i32(row.get(9)?),
                AttendanceStatus::from_i32(row.get(10)?),
            ];
            let raw_current = statuses[(period_num - 1) as usize];
            let effective_current = if raw_current == AttendanceStatus::Unmarked {
                AttendanceStatus::Present
            } else {
                raw_current
            };
            Ok(StudentAttendanceRow {
                student_id: row.get(0)?,
                row_num: row.get(1)?,
                first_name: row.get(2)?,
                last_name: row.get(3)?,
                father_name: row.get(4)?,
                national_id: row.get(5)?,
                mobile: row.get(6)?,
                current_status: effective_current,
                period_statuses: statuses,
                note: row.get(11)?,
            })
        })
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let is_period_saved = students
        .iter()
        .any(|s| s.period_statuses[(period_num - 1) as usize] != AttendanceStatus::Unmarked);

    students.sort_by(|a, b| {
        persian_sort_key(&a.last_name)
            .cmp(&persian_sort_key(&b.last_name))
            .then_with(|| persian_sort_key(&a.first_name).cmp(&persian_sort_key(&b.first_name)))
    });

    let mut summary = PeriodSummary {
        total: students.len() as i32,
        present: 0,
        absent: 0,
        late: 0,
        excused: 0,
        unmarked: 0,
    };
    for s in &students {
        match s.current_status {
            AttendanceStatus::Present => summary.present += 1,
            AttendanceStatus::Absent => summary.absent += 1,
            AttendanceStatus::Late => summary.late += 1,
            AttendanceStatus::Excused => summary.excused += 1,
            AttendanceStatus::Unmarked => summary.unmarked += 1,
        }
    }

    Ok(ClassAttendanceSnapshot {
        jalali_date: format_iso_to_jalali(date_iso),
        is_period_saved,
        summary,
        students,
    })
}

pub fn set_attendance(
    conn: &mut Connection,
    student_id: i64,
    date_iso: &str,
    period: Period,
    status: AttendanceStatus,
    note: &str,
    teacher_name: &str,
    lesson_name: &str,
    class_time: &str,
) -> Result<(), CoreError> {
    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    let now = now_unix();
    let p_num = period.to_i32();

    tx.execute(
        "INSERT OR IGNORE INTO attendance
            (student_id, date_iso, period, status, note, teacher_name, lesson_name, class_time, updated_at)
         SELECT s2.id, ?2, ?3, 1, '', ?4, ?5, ?6, ?7
         FROM students s1
         INNER JOIN students s2
             ON s2.school_name = s1.school_name
            AND s2.major = s1.major
            AND s2.grade = s1.grade
            AND s2.section = s1.section
         WHERE s1.id = ?1",
        params![student_id, date_iso, p_num, teacher_name.trim(), lesson_name.trim(), class_time.trim(), now],
    )
    .map_err(|e| CoreError::Database(e.to_string()))?;

    tx.execute(
        "INSERT INTO attendance
            (student_id, date_iso, period, status, note, teacher_name, lesson_name, class_time, updated_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
             status = excluded.status,
             note = excluded.note,
             teacher_name = excluded.teacher_name,
             lesson_name = excluded.lesson_name,
             class_time = excluded.class_time,
             updated_at = excluded.updated_at",
        params![
            student_id, date_iso, p_num, status.to_i32(), note.trim(),
            teacher_name.trim(), lesson_name.trim(), class_time.trim(), now
        ],
    )
    .map_err(|e| CoreError::Database(e.to_string()))?;

    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn mark_class_status(
    conn: &Connection,
    school_name: &str,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
    period: Period,
    status: AttendanceStatus,
    only_unmarked: bool,
    teacher_name: &str,
    lesson_name: &str,
    class_time: &str,
) -> Result<i32, CoreError> {
    let keep_existing = if only_unmarked { 1 } else { 0 };
    let changed = conn
        .execute(
            "INSERT INTO attendance
                (student_id, date_iso, period, status, note, teacher_name, lesson_name, class_time, updated_at)
             SELECT id, ?1, ?2, ?3, '', ?4, ?5, ?6, ?7
             FROM students
             WHERE school_name = ?8 AND major = ?9 AND grade = ?10 AND section = ?11
             ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
                 status = CASE
                     WHEN ?12 = 1 AND attendance.status != 0 THEN attendance.status
                     ELSE excluded.status
                 END,
                 teacher_name = excluded.teacher_name,
                 lesson_name = excluded.lesson_name,
                 class_time = excluded.class_time,
                 updated_at = excluded.updated_at",
            params![
                date_iso, period.to_i32(), status.to_i32(),
                teacher_name.trim(), lesson_name.trim(), class_time.trim(), now_unix(),
                school_name, major, grade, section, keep_existing
            ],
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(changed as i32)
}

pub fn copy_from_previous_period(
    conn: &Connection,
    school_name: &str,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
    target_period: Period,
) -> Result<i32, CoreError> {
    let prev = target_period
        .previous()
        .ok_or_else(|| CoreError::InvalidInput("زنگ اول، زنگ قبلی ندارد".into()))?;
    let copied = conn
        .execute(
            "INSERT INTO attendance
                (student_id, date_iso, period, status, note, teacher_name, lesson_name, class_time, updated_at)
             SELECT a.student_id, a.date_iso, ?1, a.status, a.note, a.teacher_name, a.lesson_name, a.class_time, ?2
             FROM attendance a
             INNER JOIN students s ON s.id = a.student_id
             WHERE a.date_iso = ?3 AND a.period = ?4
               AND s.school_name = ?5 AND s.major = ?6 AND s.grade = ?7 AND s.section = ?8
             ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
                 status = excluded.status,
                 note = excluded.note,
                 updated_at = excluded.updated_at",
            params![target_period.to_i32(), now_unix(), date_iso, prev.to_i32(), school_name, major, grade, section],
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(copied as i32)
}

pub fn add_student(
    conn: &Connection,
    school_name: &str,
    major: &str,
    grade: &str,
    section: i32,
    first_name: &str,
    last_name: &str,
    father_name: &str,
    national_id: &str,
    mobile: &str,
) -> Result<i64, CoreError> {
    let f = first_name.trim();
    let l = last_name.trim();
    let nid = normalize_national_id(national_id);
    if f.is_empty() || l.is_empty() {
        return Err(CoreError::InvalidInput("نام و نام خانوادگی الزامی است".into()));
    }
    if nid.len() != 10 {
        return Err(CoreError::InvalidInput("کد ملی باید دقیقاً ۱۰ رقم باشد".into()));
    }
    let school = if school_name.trim().is_empty() { "مدرسه" } else { school_name.trim() };
    let clean_major = if is_middle_grade(grade) { "" } else { major.trim() };
    let mob = normalize_mobile(mobile);
    let search_key = normalize_persian(&format!("{f} {l} {} {nid} {mob}", father_name.trim()));

    conn.execute(
        "INSERT INTO students
            (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, search_key)
         VALUES (0, ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)",
        params![school, clean_major, grade.trim(), section.max(1), f, l, father_name.trim(), nid, mob, search_key],
    )
    .map_err(|e| {
        if e.to_string().contains("UNIQUE") {
            CoreError::InvalidInput("دانش‌آموزی با این کد ملی در این مدرسه قبلاً ثبت شده است".into())
        } else {
            CoreError::Database(e.to_string())
        }
    })?;
    Ok(conn.last_insert_rowid())
}

pub fn update_student(
    conn: &Connection,
    student_id: i64,
    first_name: &str,
    last_name: &str,
    father_name: &str,
    national_id: &str,
    mobile: &str,
) -> Result<(), CoreError> {
    let f = first_name.trim();
    let l = last_name.trim();
    let nid = normalize_national_id(national_id);
    if f.is_empty() || l.is_empty() {
        return Err(CoreError::InvalidInput("نام و نام خانوادگی الزامی است".into()));
    }
    if nid.len() != 10 {
        return Err(CoreError::InvalidInput("کد ملی باید دقیقاً ۱۰ رقم باشد".into()));
    }
    let mob = normalize_mobile(mobile);
    let search_key = normalize_persian(&format!("{f} {l} {} {nid} {mob}", father_name.trim()));
    conn.execute(
        "UPDATE students
         SET first_name = ?1, last_name = ?2, father_name = ?3, national_id = ?4, mobile = ?5, search_key = ?6
         WHERE id = ?7",
        params![f, l, father_name.trim(), nid, mob, search_key, student_id],
    )
    .map_err(|e| {
        if e.to_string().contains("UNIQUE") {
            CoreError::InvalidInput("این کد ملی متعلق به دانش‌آموز دیگری در همین مدرسه است".into())
        } else {
            CoreError::Database(e.to_string())
        }
    })?;
    Ok(())
}

pub fn delete_student(conn: &Connection, student_id: i64) -> Result<(), CoreError> {
    conn.execute("DELETE FROM students WHERE id = ?1", params![student_id])
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn delete_class(conn: &Connection, school_name: &str, major: &str, grade: &str, section: i32) -> Result<i32, CoreError> {
    let deleted = conn
        .execute(
            "DELETE FROM students WHERE school_name = ?1 AND major = ?2 AND grade = ?3 AND section = ?4",
            params![school_name, major, grade, section],
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(deleted as i32)
}

pub fn get_class_analytics(conn: &Connection, school_name: &str, major: &str, grade: &str, section: i32) -> Result<ClassAnalytics, CoreError> {
    let mut s_stmt = conn
        .prepare_cached("SELECT id, first_name, last_name FROM students WHERE school_name = ?1 AND major = ?2 AND grade = ?3 AND section = ?4")
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut names: HashMap<i64, String> = HashMap::new();
    let rows = s_stmt
        .query_map(params![school_name, major, grade, section], |r| {
            Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, String>(2)?))
        })
        .map_err(|e| CoreError::Database(e.to_string()))?;
    for row in rows {
        let (id, f, l) = row.map_err(|e| CoreError::Database(e.to_string()))?;
        names.insert(id, format!("{f} {l}"));
    }

    let mut a_stmt = conn
        .prepare_cached(
            "SELECT a.student_id, a.date_iso, a.period, a.status
             FROM attendance a INNER JOIN students s ON s.id = a.student_id
             WHERE s.school_name = ?1 AND s.major = ?2 AND s.grade = ?3 AND s.section = ?4 AND a.status != 0",
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut sessions: HashSet<(String, i32)> = HashSet::new();
    let mut total_absent = 0i32;
    let mut total_late = 0i32;
    let mut total_excused = 0i32;
    let mut abs_map: HashMap<i64, i32> = HashMap::new();
    let mut late_map: HashMap<i64, i32> = HashMap::new();
    let mut exc_map: HashMap<i64, i32> = HashMap::new();

    let a_rows = a_stmt
        .query_map(params![school_name, major, grade, section], |r| {
            Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?)))
        })
        .map_err(|e| CoreError::Database(e.to_string()))?;

    for row in a_rows {
        let (sid, date, period, st) = row.map_err(|e| CoreError::Database(e.to_string()))?;
        sessions.insert((date, period));
        match st {
            AttendanceStatus::Absent => { total_absent += 1; *abs_map.entry(sid).or_default() += 1; }
            AttendanceStatus::Late => { total_late += 1; *late_map.entry(sid).or_default() += 1; }
            AttendanceStatus::Excused => { total_excused += 1; *exc_map.entry(sid).or_default() += 1; }
            _ => {}
        }
    }

    let rank = |m: HashMap<i64, i32>| -> Vec<TopStudentCount> {
        let mut v: Vec<TopStudentCount> = m
            .into_iter()
            .filter_map(|(sid, count)| names.get(&sid).map(|n| TopStudentCount { full_name: n.clone(), count }))
            .collect();
        v.sort_by(|a, b| b.count.cmp(&a.count).then_with(|| persian_sort_key(&a.full_name).cmp(&persian_sort_key(&b.full_name))));
        v.truncate(8);
        v
    };

    Ok(ClassAnalytics {
        student_count: names.len() as i32,
        recorded_sessions: sessions.len() as i32,
        total_absent,
        total_late,
        total_excused,
        top_absent: rank(abs_map),
        top_late: rank(late_map),
        top_excused: rank(exc_map),
    })
}

pub fn get_monthly_report(
    conn: &Connection,
    school_name: &str,
    major: &str,
    grade: &str,
    section: i32,
    jalali_year: i32,
    jalali_month: i32,
) -> Result<MonthlyClassReport, CoreError> {
    let jm = jalali_month.clamp(1, 12) as u32;
    let (start_iso, end_iso) = jalali_month_range_iso(jalali_year, jm);

    let mut s_stmt = conn
        .prepare_cached("SELECT id, first_name, last_name, father_name, national_id, mobile FROM students WHERE school_name = ?1 AND major = ?2 AND grade = ?3 AND section = ?4")
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut base_students: Vec<(i64, String, String, String, String, String)> = s_stmt
        .query_map(params![school_name, major, grade, section], |r| {
            Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?, r.get(5)?))
        })
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    base_students.sort_by(|a, b| {
        persian_sort_key(&a.2).cmp(&persian_sort_key(&b.2)).then_with(|| persian_sort_key(&a.1).cmp(&persian_sort_key(&b.1)))
    });

    let mut a_stmt = conn
        .prepare_cached(
            "SELECT a.student_id, a.date_iso, a.period, a.status
             FROM attendance a INNER JOIN students s ON s.id = a.student_id
             WHERE s.school_name = ?1 AND s.major = ?2 AND s.grade = ?3 AND s.section = ?4
               AND a.date_iso >= ?5 AND a.date_iso <= ?6 AND a.status != 0",
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut active_periods_by_date: HashMap<String, HashSet<i32>> = HashMap::new();
    let mut student_day_statuses: HashMap<(i64, String), HashMap<i32, AttendanceStatus>> = HashMap::new();

    let rows = a_stmt
        .query_map(params![school_name, major, grade, section, start_iso, end_iso], |r| {
            Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?)))
        })
        .map_err(|e| CoreError::Database(e.to_string()))?;

    for row in rows {
        let (sid, date_iso, period, status) = row.map_err(|e| CoreError::Database(e.to_string()))?;
        active_periods_by_date.entry(date_iso.clone()).or_default().insert(period);
        student_day_statuses.entry((sid, date_iso)).or_default().insert(period, status);
    }

    let recorded_days = active_periods_by_date.len() as i32;
    let mut total_absent_periods = 0i32;
    let mut total_full_absent_days = 0i32;
    let mut sum_percents = 0.0f64;
    let mut percent_count = 0i32;
    let mut stats = Vec::with_capacity(base_students.len());

    for (sid, first_name, last_name, father_name, national_id, mobile) in base_students {
        let (mut present_p, mut absent_p, mut late_p, mut excused_p, mut full_abs_days) = (0, 0, 0, 0, 0);
        for (date_iso, active_periods) in &active_periods_by_date {
            if let Some(day_map) = student_day_statuses.get(&(sid, date_iso.clone())) {
                for st in day_map.values() {
                    match st {
                        AttendanceStatus::Present => present_p += 1,
                        AttendanceStatus::Absent => absent_p += 1,
                        AttendanceStatus::Late => late_p += 1,
                        AttendanceStatus::Excused => excused_p += 1,
                        AttendanceStatus::Unmarked => {}
                    }
                }
                if active_periods.len() >= 2 {
                    let all_abs_or_exc = active_periods.iter().all(|p| matches!(day_map.get(p), Some(AttendanceStatus::Absent | AttendanceStatus::Excused)));
                    let has_unexcused = active_periods.iter().any(|p| matches!(day_map.get(p), Some(AttendanceStatus::Absent)));
                    if all_abs_or_exc && has_unexcused { full_abs_days += 1; }
                }
            }
        }
        let total_marked = present_p + absent_p + late_p + excused_p;
        let attendance_percent = if total_marked > 0 {
            let pct = ((present_p + late_p) as f64 / total_marked as f64) * 100.0;
            sum_percents += pct;
            percent_count += 1;
            (pct * 10.0).round() / 10.0
        } else { 100.0 };

        total_absent_periods += absent_p;
        total_full_absent_days += full_abs_days;
        stats.push(MonthlyStudentStat {
            student_id: sid, first_name, last_name, father_name, national_id, mobile,
            present_periods: present_p, absent_periods: absent_p, full_absent_days: full_abs_days,
            late_periods: late_p, excused_periods: excused_p, attendance_percent,
        });
    }

    let average_attendance_percent = if percent_count > 0 {
        ((sum_percents / percent_count as f64) * 10.0).round() / 10.0
    } else { 100.0 };

    Ok(MonthlyClassReport {
        jalali_year, jalali_month,
        month_label: format_jalali_month_label(jalali_year, jm),
        recorded_days, average_attendance_percent, total_absent_periods, total_full_absent_days,
        students: stats,
    })
}

#[derive(Serialize, Deserialize)]
struct BackupPayload {
    version: i32,
    students: Vec<BackupStudent>,
    attendance: Vec<BackupAttendance>,
    settings: HashMap<String, String>,
}

#[derive(Serialize, Deserialize)]
struct BackupStudent {
    row_num: i32, school_name: String, major: String, grade: String, section: i32,
    first_name: String, last_name: String, father_name: String, national_id: String, mobile: String,
}

#[derive(Serialize, Deserialize)]
struct BackupAttendance {
    school_name: String, national_id: String, date_iso: String, period: i32,
    status: i32, note: String, teacher_name: String, lesson_name: String, class_time: String,
}

pub fn export_backup_json(conn: &Connection) -> Result<String, CoreError> {
    let mut s_stmt = conn
        .prepare("SELECT row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile FROM students")
        .map_err(|e| CoreError::Database(e.to_string()))?;
    let students: Vec<BackupStudent> = s_stmt
        .query_map([], |r| Ok(BackupStudent {
            row_num: r.get(0)?, school_name: r.get(1)?, major: r.get(2)?, grade: r.get(3)?, section: r.get(4)?,
            first_name: r.get(5)?, last_name: r.get(6)?, father_name: r.get(7)?, national_id: r.get(8)?, mobile: r.get(9)?,
        }))
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut a_stmt = conn
        .prepare("SELECT s.school_name, s.national_id, a.date_iso, a.period, a.status, a.note, a.teacher_name, a.lesson_name, a.class_time FROM attendance a INNER JOIN students s ON s.id = a.student_id")
        .map_err(|e| CoreError::Database(e.to_string()))?;
    let attendance: Vec<BackupAttendance> = a_stmt
        .query_map([], |r| Ok(BackupAttendance {
            school_name: r.get(0)?, national_id: r.get(1)?, date_iso: r.get(2)?, period: r.get(3)?,
            status: r.get(4)?, note: r.get(5)?, teacher_name: r.get(6)?, lesson_name: r.get(7)?, class_time: r.get(8)?,
        }))
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut set_stmt = conn.prepare("SELECT key, value FROM app_settings").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut settings = HashMap::new();
    for r in set_stmt.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?))).map_err(|e| CoreError::Database(e.to_string()))? {
        let (k, v) = r.map_err(|e| CoreError::Database(e.to_string()))?;
        settings.insert(k, v);
    }

    serde_json::to_string_pretty(&BackupPayload { version: 2, students, attendance, settings })
        .map_err(|e| CoreError::Import(e.to_string()))
}

pub fn restore_backup_json(conn: &mut Connection, json_text: &str) -> Result<ImportReport, CoreError> {
    let payload: BackupPayload = serde_json::from_str(json_text.trim_start_matches('\u{FEFF}'))
        .map_err(|e| CoreError::Import(format!("فایل پشتیبان JSON معتبر نیست: {e}")))?;

    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    tx.execute("DELETE FROM attendance", []).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.execute("DELETE FROM students", []).map_err(|e| CoreError::Database(e.to_string()))?;

    let mut id_map: HashMap<(String, String), i64> = HashMap::new();
    {
        let mut stmt = tx
            .prepare_cached("INSERT INTO students (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, search_key) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)")
            .map_err(|e| CoreError::Database(e.to_string()))?;
        for s in &payload.students {
            let search_key = normalize_persian(&format!("{} {} {} {} {}", s.first_name, s.last_name, s.father_name, s.national_id, s.mobile));
            stmt.execute(params![s.row_num, s.school_name, s.major, s.grade, s.section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, search_key])
                .map_err(|e| CoreError::Database(e.to_string()))?;
            id_map.insert((s.school_name.clone(), s.national_id.clone()), tx.last_insert_rowid());
        }
    }

    {
        let mut a_stmt = tx
            .prepare_cached("INSERT OR REPLACE INTO attendance (student_id, date_iso, period, status, note, teacher_name, lesson_name, class_time, updated_at) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)")
            .map_err(|e| CoreError::Database(e.to_string()))?;
        let now = now_unix();
        for a in &payload.attendance {
            if let Some(&sid) = id_map.get(&(a.school_name.clone(), a.national_id.clone())) {
                let _ = a_stmt.execute(params![sid, a.date_iso, a.period, a.status, a.note, a.teacher_name, a.lesson_name, a.class_time, now]);
            }
        }
    }

    for (k, v) in &payload.settings {
        let _ = tx.execute("INSERT INTO app_settings (key, value) VALUES (?1, ?2) ON CONFLICT(key) DO UPDATE SET value = excluded.value", params![k, v]);
    }

    let classes_count: i32 = tx
        .query_row("SELECT COUNT(*) FROM (SELECT DISTINCT school_name, major, grade, section FROM students)", [], |r| r.get(0))
        .map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(ImportReport { imported_count: payload.students.len() as i32, skipped_count: 0, classes_count })
}

fn now_unix() -> i64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0)
}
