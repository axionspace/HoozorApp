use crate::models::{
    AttendanceStatus, ClassAttendanceSnapshot, ClassGroup, CoreError, MonthlyClassReport,
    MonthlyStudentStat, Period, PeriodSummary, StudentAttendanceRow,
};
use crate::persian::{
    format_iso_to_jalali, format_jalali_month_label, grade_rank, jalali_month_range_iso,
    normalize_persian, persian_sort_key,
};
use rusqlite::{params, Connection};
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
             national_id TEXT NOT NULL UNIQUE,
             mobile      TEXT NOT NULL,
             search_key  TEXT NOT NULL
         );

         CREATE TABLE IF NOT EXISTS attendance (
             student_id  INTEGER NOT NULL,
             date_iso    TEXT NOT NULL,
             period      INTEGER NOT NULL CHECK(period BETWEEN 1 AND 4),
             status      INTEGER NOT NULL,
             note        TEXT NOT NULL DEFAULT '',
             updated_at  INTEGER NOT NULL,
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
        .prepare_cached(
            "SELECT school_name, major, grade, section, COUNT(*) as cnt
             FROM students
             GROUP BY major, grade, section",
        )
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
        persian_sort_key(&a.major)
            .cmp(&persian_sort_key(&b.major))
            .then_with(|| grade_rank(&a.grade).cmp(&grade_rank(&b.grade)))
            .then_with(|| a.section.cmp(&b.section))
    });
    Ok(classes)
}

pub fn get_class_attendance(
    conn: &Connection,
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
                 COALESCE(MAX(CASE WHEN a.period = ?5 THEN a.note END), '') AS cur_note
             FROM students s
             LEFT JOIN attendance a ON a.student_id = s.id AND a.date_iso = ?4
             WHERE s.major = ?1 AND s.grade = ?2 AND s.section = ?3
               AND (?6 = '' OR s.search_key LIKE ?6)
             GROUP BY s.id",
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut students: Vec<StudentAttendanceRow> = stmt
        .query_map(params![major, grade, section, date_iso, period_num, like_pattern], |row| {
            let statuses = vec![
                AttendanceStatus::from_i32(row.get(7)?),
                AttendanceStatus::from_i32(row.get(8)?),
                AttendanceStatus::from_i32(row.get(9)?),
                AttendanceStatus::from_i32(row.get(10)?),
            ];
            let current_status = statuses[(period_num - 1) as usize];
            Ok(StudentAttendanceRow {
                student_id: row.get(0)?,
                row_num: row.get(1)?,
                first_name: row.get(2)?,
                last_name: row.get(3)?,
                father_name: row.get(4)?,
                national_id: row.get(5)?,
                mobile: row.get(6)?,
                current_status,
                period_statuses: statuses,
                note: row.get(11)?,
            })
        })
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

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
        summary,
        students,
    })
}

pub fn set_attendance(
    conn: &Connection,
    student_id: i64,
    date_iso: &str,
    period: Period,
    status: AttendanceStatus,
    note: &str,
) -> Result<(), CoreError> {
    conn.execute(
        "INSERT INTO attendance (student_id, date_iso, period, status, note, updated_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6)
         ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
             status = excluded.status,
             note = excluded.note,
             updated_at = excluded.updated_at",
        params![student_id, date_iso, period.to_i32(), status.to_i32(), note.trim(), now_unix()],
    )
    .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(())
}

pub fn mark_class_status(
    conn: &Connection,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
    period: Period,
    status: AttendanceStatus,
    only_unmarked: bool,
) -> Result<i32, CoreError> {
    let keep_existing = if only_unmarked { 1 } else { 0 };
    let changed = conn
        .execute(
            "INSERT INTO attendance (student_id, date_iso, period, status, note, updated_at)
             SELECT id, ?1, ?2, ?3, '', ?4
             FROM students
             WHERE major = ?5 AND grade = ?6 AND section = ?7
             ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
                 status = CASE
                     WHEN ?8 = 1 AND attendance.status != 0 THEN attendance.status
                     ELSE excluded.status
                 END,
                 updated_at = excluded.updated_at",
            params![date_iso, period.to_i32(), status.to_i32(), now_unix(), major, grade, section, keep_existing],
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(changed as i32)
}

pub fn copy_from_previous_period(
    conn: &Connection,
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
            "INSERT INTO attendance (student_id, date_iso, period, status, note, updated_at)
             SELECT a.student_id, a.date_iso, ?1, a.status, a.note, ?2
             FROM attendance a
             INNER JOIN students s ON s.id = a.student_id
             WHERE a.date_iso = ?3 AND a.period = ?4
               AND s.major = ?5 AND s.grade = ?6 AND s.section = ?7
             ON CONFLICT(student_id, date_iso, period) DO UPDATE SET
                 status = excluded.status,
                 note = excluded.note,
                 updated_at = excluded.updated_at",
            params![target_period.to_i32(), now_unix(), date_iso, prev.to_i32(), major, grade, section],
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(copied as i32)
}

pub fn export_daily_csv(
    conn: &Connection,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
) -> Result<String, CoreError> {
    let snapshot = get_class_attendance(conn, major, grade, section, date_iso, Period::First, "")?;
    let mut csv = String::with_capacity(snapshot.students.len() * 140 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل,تاریخ,زنگ اول,زنگ دوم,زنگ سوم,زنگ چهارم\n");
    for (idx, s) in snapshot.students.iter().enumerate() {
        csv.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
            idx + 1, major, grade, section, s.first_name, s.last_name, s.father_name,
            s.national_id, s.mobile, snapshot.jalali_date,
            s.period_statuses[0].label_fa(),
            s.period_statuses[1].label_fa(),
            s.period_statuses[2].label_fa(),
            s.period_statuses[3].label_fa(),
        ));
    }
    Ok(csv)
}

pub fn get_monthly_report(
    conn: &Connection,
    major: &str,
    grade: &str,
    section: i32,
    jalali_year: i32,
    jalali_month: i32,
) -> Result<MonthlyClassReport, CoreError> {
    let jm = jalali_month.clamp(1, 12) as u32;
    let (start_iso, end_iso) = jalali_month_range_iso(jalali_year, jm);

    let mut s_stmt = conn
        .prepare_cached(
            "SELECT id, first_name, last_name, father_name, national_id, mobile
             FROM students
             WHERE major = ?1 AND grade = ?2 AND section = ?3",
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut base_students: Vec<(i64, String, String, String, String, String)> = s_stmt
        .query_map(params![major, grade, section], |r| {
            Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?, r.get(5)?))
        })
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;

    base_students.sort_by(|a, b| {
        persian_sort_key(&a.2)
            .cmp(&persian_sort_key(&b.2))
            .then_with(|| persian_sort_key(&a.1).cmp(&persian_sort_key(&b.1)))
    });

    let mut a_stmt = conn
        .prepare_cached(
            "SELECT a.student_id, a.date_iso, a.period, a.status
             FROM attendance a
             INNER JOIN students s ON s.id = a.student_id
             WHERE s.major = ?1 AND s.grade = ?2 AND s.section = ?3
               AND a.date_iso >= ?4 AND a.date_iso <= ?5
               AND a.status != 0",
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    let mut active_periods_by_date: HashMap<String, HashSet<i32>> = HashMap::new();
    let mut student_day_statuses: HashMap<(i64, String), HashMap<i32, AttendanceStatus>> = HashMap::new();

    let rows = a_stmt
        .query_map(params![major, grade, section, start_iso, end_iso], |r| {
            Ok((
                r.get::<_, i64>(0)?,
                r.get::<_, String>(1)?,
                r.get::<_, i32>(2)?,
                AttendanceStatus::from_i32(r.get::<_, i32>(3)?),
            ))
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
        let mut present_p = 0i32;
        let mut absent_p = 0i32;
        let mut late_p = 0i32;
        let mut excused_p = 0i32;
        let mut full_abs_days = 0i32;

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
                    let all_abs_or_exc = active_periods.iter().all(|p| {
                        matches!(day_map.get(p), Some(AttendanceStatus::Absent | AttendanceStatus::Excused))
                    });
                    let has_unexcused = active_periods
                        .iter()
                        .any(|p| matches!(day_map.get(p), Some(AttendanceStatus::Absent)));
                    if all_abs_or_exc && has_unexcused {
                        full_abs_days += 1;
                    }
                }
            }
        }

        let total_marked = present_p + absent_p + late_p + excused_p;
        let attendance_percent = if total_marked > 0 {
            let pct = ((present_p + late_p) as f64 / total_marked as f64) * 100.0;
            sum_percents += pct;
            percent_count += 1;
            (pct * 10.0).round() / 10.0
        } else {
            100.0
        };

        total_absent_periods += absent_p;
        total_full_absent_days += full_abs_days;

        stats.push(MonthlyStudentStat {
            student_id: sid,
            first_name,
            last_name,
            father_name,
            national_id,
            mobile,
            present_periods: present_p,
            absent_periods: absent_p,
            full_absent_days: full_abs_days,
            late_periods: late_p,
            excused_periods: excused_p,
            attendance_percent,
        });
    }

    let average_attendance_percent = if percent_count > 0 {
        ((sum_percents / percent_count as f64) * 10.0).round() / 10.0
    } else {
        100.0
    };

    Ok(MonthlyClassReport {
        jalali_year,
        jalali_month,
        month_label: format_jalali_month_label(jalali_year, jm),
        recorded_days,
        average_attendance_percent,
        total_absent_periods,
        total_full_absent_days,
        students: stats,
    })
}

fn now_unix() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs() as i64)
        .unwrap_or(0)
}
