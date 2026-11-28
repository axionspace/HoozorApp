from pathlib import Path

FILES = {
    "rust-core/Cargo.toml": r'''[package]
name = "hozoor_core"
version = "5.1.0"
edition = "2021"

[lib]
name = "hozoor_core"
crate-type = ["cdylib", "rlib"]

[[bin]]
name = "uniffi-bindgen"
path = "uniffi-bindgen.rs"

[dependencies]
uniffi = { version = "0.28.3", features = ["cli"] }
rusqlite = { version = "0.32.1", features = ["bundled"] }
calamine = "0.26.1"
zip = "=2.5.0"
rust_xlsxwriter = "0.80.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
thiserror = "2.0"

[profile.release]
opt-level = "z"
lto = true
codegen-units = 1
''',

    "rust-core/uniffi-bindgen.rs": r'''fn main() { uniffi::uniffi_bindgen_main() }
''',

    "rust-core/src/models.rs": r'''use thiserror::Error;

#[derive(Debug, Error, uniffi::Error)]
#[uniffi(flat_error)]
pub enum CoreError {
    #[error("خطای پایگاه داده: {0}")]
    Database(String),
    #[error("خطای فایل: {0}")]
    Import(String),
    #[error("ورودی نامعتبر: {0}")]
    InvalidInput(String),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, uniffi::Enum)]
pub enum Period { First, Second, Third, Fourth }

impl Period {
    pub fn to_i32(self) -> i32 {
        match self { Period::First => 1, Period::Second => 2, Period::Third => 3, Period::Fourth => 4 }
    }
    pub fn from_i32(v: i32) -> Self {
        match v { 2 => Period::Second, 3 => Period::Third, 4 => Period::Fourth, _ => Period::First }
    }
    pub fn previous(self) -> Option<Period> {
        match self { Period::First => None, Period::Second => Some(Period::First), Period::Third => Some(Period::Second), Period::Fourth => Some(Period::Third) }
    }
    pub fn label_fa(self) -> &'static str {
        match self { Period::First => "زنگ اول", Period::Second => "زنگ دوم", Period::Third => "زنگ سوم", Period::Fourth => "زنگ چهارم" }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, uniffi::Enum)]
pub enum AttendanceStatus { Unmarked, Present, Absent, Late, Excused, LeftClass }

impl AttendanceStatus {
    pub fn to_i32(self) -> i32 {
        match self {
            AttendanceStatus::Unmarked => 0, AttendanceStatus::Present => 1, AttendanceStatus::Absent => 2,
            AttendanceStatus::Late => 3, AttendanceStatus::Excused => 4, AttendanceStatus::LeftClass => 5,
        }
    }
    pub fn from_i32(v: i32) -> Self {
        match v {
            1 => AttendanceStatus::Present, 2 => AttendanceStatus::Absent, 3 => AttendanceStatus::Late,
            4 => AttendanceStatus::Excused, 5 => AttendanceStatus::LeftClass, _ => AttendanceStatus::Unmarked,
        }
    }
    pub fn label_fa(self) -> &'static str {
        match self {
            AttendanceStatus::Unmarked | AttendanceStatus::Present => "حاضر",
            AttendanceStatus::Absent => "غایب",
            AttendanceStatus::Late => "تأخیر",
            AttendanceStatus::Excused => "غیبت موجه",
            AttendanceStatus::LeftClass => "خروج از کلاس",
        }
    }
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct ClassGroup { pub school_name: String, pub major: String, pub grade: String, pub section: i32, pub student_count: i32 }

#[derive(Debug, Clone, uniffi::Record)]
pub struct StudentAttendanceRow {
    pub student_id: i64, pub row_num: i32, pub first_name: String, pub last_name: String,
    pub father_name: String, pub national_id: String, pub mobile: String,
    pub current_status: AttendanceStatus, pub period_statuses: Vec<AttendanceStatus>,
    pub event_time: String, pub note: String, pub latest_grade: String,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct PeriodSummary { pub total: i32, pub present: i32, pub absent: i32, pub late: i32, pub excused: i32, pub left_class: i32 }

#[derive(Debug, Clone, uniffi::Record)]
pub struct ClassAttendanceSnapshot { pub jalali_date: String, pub is_period_saved: bool, pub summary: PeriodSummary, pub students: Vec<StudentAttendanceRow> }

#[derive(Debug, Clone, uniffi::Record)]
pub struct ImportReport { pub imported_count: i32, pub skipped_count: i32, pub classes_count: i32 }

#[derive(Debug, Clone, uniffi::Record)]
pub struct PrincipalReportBundle {
    pub full_text: String, pub sms_text: String, pub full_day_absent_count: i32,
    pub partial_absent_count: i32, pub late_count: i32, pub left_class_count: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct GradeCategory { pub id: i64, pub name: String }

#[derive(Debug, Clone, uniffi::Record)]
pub struct StudentGradeRow { pub student_id: i64, pub first_name: String, pub last_name: String, pub father_name: String, pub score: String, pub note: String }

#[derive(Debug, Clone, uniffi::Record)]
pub struct SavedContact { pub id: i64, pub name: String, pub role: String, pub phone: String }

#[derive(Debug, Clone, uniffi::Record)]
pub struct BackupStats { pub students_count: i32, pub classes_count: i32, pub attendance_count: i32, pub grades_count: i32, pub contacts_count: i32 }

#[derive(Debug, Clone, uniffi::Record)]
pub struct TopStudentCount { pub full_name: String, pub count: i32 }

#[derive(Debug, Clone, uniffi::Record)]
pub struct ClassAnalytics {
    pub student_count: i32, pub recorded_sessions: i32, pub total_absent: i32,
    pub total_late: i32, pub total_excused: i32, pub total_left_class: i32,
    pub top_absent: Vec<TopStudentCount>, pub top_late: Vec<TopStudentCount>,
    pub top_excused: Vec<TopStudentCount>, pub top_left_class: Vec<TopStudentCount>,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct StudentMonthlyEvent {
    pub date_iso: String, pub jalali_date: String, pub period_label: String,
    pub status: AttendanceStatus, pub event_time: String, pub note: String,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct MonthlyStudentStat {
    pub student_id: i64, pub first_name: String, pub last_name: String, pub father_name: String,
    pub national_id: String, pub mobile: String, pub present_periods: i32, pub absent_periods: i32,
    pub full_absent_days: i32, pub late_periods: i32, pub excused_periods: i32, pub left_class_periods: i32,
    pub attendance_percent: f64,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct MonthlyClassReport {
    pub jalali_year: i32, pub jalali_month: i32, pub month_label: String, pub recorded_days: i32,
    pub average_attendance_percent: f64, pub total_absent_periods: i32, pub total_full_absent_days: i32,
    pub total_left_class: i32, pub students: Vec<MonthlyStudentStat>,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct JalaliYearMonth { pub year: i32, pub month: i32, pub label: String }

#[derive(Debug, Clone, uniffi::Record)]
pub struct JalaliDayCell { pub day: i32, pub date_iso: String, pub is_friday: bool }

#[derive(Debug, Clone, uniffi::Record)]
pub struct JalaliMonthGrid { pub year: i32, pub month: i32, pub month_label: String, pub leading_blanks: i32, pub days: Vec<JalaliDayCell> }
''',

    "rust-core/src/persian.rs": r'''use crate::models::{JalaliDayCell, JalaliMonthGrid};

pub fn normalize_persian(input: &str) -> String {
    let mut out = String::with_capacity(input.len());
    for ch in input.trim().chars() {
        let m = match ch {
            'ي' | 'ى' => 'ی', 'ك' => 'ک', 'ة' | 'ۀ' => 'ه', 'ؤ' => 'و', 'إ' | 'أ' => 'ا',
            '۰' | '٠' => '0', '۱' | '١' => '1', '۲' | '٢' => '2', '۳' | '٣' => '3', '۴' | '٤' => '4',
            '۵' | '٥' => '5', '۶' | '٦' => '6', '۷' | '٧' => '7', '۸' | '٨' => '8', '۹' | '٩' => '9',
            '\u{0640}' | '\u{064B}'..='\u{065F}' => continue, _ => ch,
        };
        out.push(m);
    }
    out.to_lowercase()
}

pub fn to_persian_digits(input: &str) -> String {
    input.chars().map(|c| match c {
        '0' => '۰', '1' => '۱', '2' => '۲', '3' => '۳', '4' => '۴',
        '5' => '۵', '6' => '۶', '7' => '۷', '8' => '۸', '9' => '۹', _ => c,
    }).collect()
}

pub fn persian_sort_key(input: &str) -> Vec<u8> {
    normalize_persian(input).chars().map(|c| match c {
        ' ' | '\u{200C}' => 1, 'آ' => 2, 'ا' => 3, 'ب' => 4, 'پ' => 5, 'ت' => 6, 'ث' => 7,
        'ج' => 8, 'چ' => 9, 'ح' => 10, 'خ' => 11, 'د' => 12, 'ذ' => 13, 'ر' => 14, 'ز' => 15,
        'ژ' => 16, 'س' => 17, 'ش' => 18, 'ص' => 19, 'ض' => 20, 'ط' => 21, 'ظ' => 22, 'ع' => 23,
        'غ' => 24, 'ف' => 25, 'ق' => 26, 'ک' => 27, 'گ' => 28, 'ل' => 29, 'م' => 30, 'ن' => 31,
        'و' => 32, 'ه' => 33, 'ی' | 'ئ' => 34, '0'..='9' => 40 + (c as u8 - b'0'), _ => 100,
    }).collect()
}

pub fn normalize_national_id(raw: &str) -> String {
    let d: String = normalize_persian(raw).chars().filter(|c| c.is_ascii_digit()).collect();
    if d.is_empty() { String::new() } else if d.len() < 10 { format!("{:0>10}", d) } else { d.chars().take(10).collect() }
}

pub fn normalize_mobile(raw: &str) -> String {
    let d: String = normalize_persian(raw).chars().filter(|c| c.is_ascii_digit()).collect();
    if d.len() == 10 && d.starts_with('9') { format!("0{d}") }
    else if d.len() == 12 && d.starts_with("98") { format!("0{}", &d[2..]) }
    else if d.len() == 14 && d.starts_with("0098") { format!("0{}", &d[4..]) }
    else { d }
}

pub fn grade_rank(g: &str) -> i32 {
    match normalize_persian(g).as_str() {
        "اول" => 1, "دوم" => 2, "سوم" => 3, "چهارم" => 4, "پنجم" => 5, "ششم" => 6,
        "هفتم" => 7, "هشتم" => 8, "نهم" => 9, "دهم" => 10, "یازدهم" => 11, "دوازدهم" => 12, _ => 99,
    }
}

pub fn is_middle_grade(g: &str) -> bool { matches!(normalize_persian(g).as_str(), "هفتم" | "هشتم" | "نهم") }

pub fn format_iso_to_jalali(iso: &str) -> String {
    let p: Vec<&str> = iso.split('-').collect();
    if p.len() != 3 { return to_persian_digits(iso); }
    let (Ok(gy), Ok(gm), Ok(gd)) = (p[0].parse::<i32>(), p[1].parse::<u32>(), p[2].parse::<u32>()) else { return to_persian_digits(iso); };
    if !(1..=12).contains(&gm) || !(1..=31).contains(&gd) { return to_persian_digits(iso); }
    let (jy, jm, jd) = gregorian_to_jalali(gy, gm, gd);
    to_persian_digits(&format!("{} {jd} {} {jy}", weekday_fa(gy, gm, gd), month_name_fa(jm)))
}

pub fn format_iso_to_jalali_short(iso: &str) -> String {
    let p: Vec<&str> = iso.split('-').collect();
    if p.len() == 3 {
        if let (Ok(gy), Ok(gm), Ok(gd)) = (p[0].parse::<i32>(), p[1].parse::<u32>(), p[2].parse::<u32>()) {
            let (jy, jm, jd) = gregorian_to_jalali(gy, gm, gd);
            return to_persian_digits(&format!("{jd} {} {jy}", month_name_fa(jm)));
        }
    }
    to_persian_digits(iso)
}

pub fn iso_to_jalali_year_month(iso: &str) -> (i32, u32) {
    let p: Vec<&str> = iso.split('-').collect();
    if p.len() == 3 {
        if let (Ok(gy), Ok(gm), Ok(gd)) = (p[0].parse::<i32>(), p[1].parse::<u32>(), p[2].parse::<u32>()) {
            let (jy, jm, _) = gregorian_to_jalali(gy, gm, gd);
            return (jy, jm);
        }
    }
    (1404, 7)
}

pub fn gregorian_to_jalali(gy: i32, gm: u32, gd: u32) -> (i32, u32, u32) {
    let g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    let gy2 = if gm > 2 { gy + 1 } else { gy };
    let mut days = 355666 + (365 * gy) + ((gy2 + 3) / 4) - ((gy2 + 99) / 100) + ((gy2 + 399) / 400) + gd as i32 + g_d_m[(gm - 1) as usize];
    let mut jy = -1595 + (33 * (days / 12053));
    days %= 12053;
    jy += 4 * (days / 1461);
    days %= 1461;
    if days > 365 { jy += (days - 1) / 365; days = (days - 1) % 365; }
    let (jm, jd) = if days < 186 { (1 + (days / 31) as u32, 1 + (days % 31) as u32) } else { (7 + ((days - 186) / 30) as u32, 1 + ((days - 186) % 30) as u32) };
    (jy, jm, jd)
}

pub fn jalali_to_gregorian(jy: i32, jm: u32, jd: u32) -> (i32, u32, u32) {
    let jy2 = jy + 1595;
    let mut days = -355668 + (365 * jy2) + ((jy2 / 33) * 8) + (((jy2 % 33) + 3) / 4) + jd as i32 + if jm < 7 { (jm as i32 - 1) * 31 } else { ((jm as i32 - 7) * 30) + 186 };
    let mut gy = 400 * (days / 146097);
    days %= 146097;
    if days > 36524 { days -= 1; gy += 100 * (days / 36524); days %= 36524; if days >= 365 { days += 1; } }
    gy += 4 * (days / 1461);
    days %= 1461;
    if days > 365 { gy += (days - 1) / 365; days = (days - 1) % 365; }
    let mut gd = days + 1;
    let leap = (gy % 4 == 0 && gy % 100 != 0) || (gy % 400 == 0);
    let sal = [0, 31, if leap { 29 } else { 28 }, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let mut gm = 1u32;
    while gm <= 12 && gd > sal[gm as usize] { gd -= sal[gm as usize]; gm += 1; }
    (gy, gm, gd as u32)
}

pub fn jalali_month_days(jy: i32, jm: u32) -> u32 {
    match jm {
        1..=6 => 31, 7..=11 => 30,
        12 => { let (gy, gm, gd) = jalali_to_gregorian(jy, 12, 30); if gregorian_to_jalali(gy, gm, gd) == (jy, 12, 30) { 30 } else { 29 } }
        _ => 30,
    }
}

pub fn jalali_month_range_iso(jy: i32, jm: u32) -> (String, String) {
    let last = jalali_month_days(jy, jm);
    let (sy, sm, sd) = jalali_to_gregorian(jy, jm, 1);
    let (ey, em, ed) = jalali_to_gregorian(jy, jm, last);
    (format!("{sy:04}-{sm:02}-{sd:02}"), format!("{ey:04}-{em:02}-{ed:02}"))
}

pub fn format_jalali_month_label(jy: i32, jm: u32) -> String { to_persian_digits(&format!("{} {}", month_name_fa(jm), jy)) }

pub fn build_jalali_month_grid(jy: i32, jm_i32: i32) -> JalaliMonthGrid {
    let jm = jm_i32.clamp(1, 12) as u32;
    let total = jalali_month_days(jy, jm);
    let (fy, fm, fd) = jalali_to_gregorian(jy, jm, 1);
    let blanks = (sun_wd(fy, fm, fd) + 1) % 7;
    let mut days = Vec::with_capacity(total as usize);
    for d in 1..=total {
        let (gy, gm, gd) = jalali_to_gregorian(jy, jm, d);
        days.push(JalaliDayCell { day: d as i32, date_iso: format!("{gy:04}-{gm:02}-{gd:02}"), is_friday: (sun_wd(gy, gm, gd) + 1) % 7 == 6 });
    }
    JalaliMonthGrid { year: jy, month: jm as i32, month_label: format_jalali_month_label(jy, jm), leading_blanks: blanks as i32, days }
}

fn sun_wd(y: i32, m: u32, d: u32) -> usize {
    let t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4];
    let y = if m < 3 { y - 1 } else { y };
    (y + y / 4 - y / 100 + y / 400 + t[(m - 1) as usize] + d as i32).rem_euclid(7) as usize
}

fn weekday_fa(y: i32, m: u32, d: u32) -> &'static str {
    ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"][sun_wd(y, m, d)]
}

pub fn month_name_fa(m: u32) -> &'static str {
    match m {
        1 => "فروردین", 2 => "اردیبهشت", 3 => "خرداد", 4 => "تیر", 5 => "مرداد", 6 => "شهریور",
        7 => "مهر", 8 => "آبان", 9 => "آذر", 10 => "دی", 11 => "بهمن", 12 => "اسفند", _ => "",
    }
}
''',

    "rust-core/src/importer.rs": r'''use crate::models::{CoreError, ImportReport};
use crate::persian::{is_middle_grade, normalize_mobile, normalize_national_id, normalize_persian};
use calamine::{open_workbook_auto_from_rs, Data, Reader};
use rusqlite::{params, Connection};
use std::io::Cursor;

pub fn import_file_bytes(conn: &mut Connection, file_name: &str, bytes: &[u8], replace_existing: bool) -> Result<ImportReport, CoreError> {
    if bytes.is_empty() { return Err(CoreError::Import("فایل انتخاب‌شده خالی است".into())); }
    let low = file_name.to_lowercase();
    let is_excel = (bytes.len() >= 4 && (&bytes[0..4] == b"PK\x03\x04" || &bytes[0..4] == b"\xD0\xCF\x11\xE0")) || low.ends_with(".xlsx") || low.ends_with(".xls");
    let rows: Vec<Vec<String>> = if is_excel {
        let mut wb = open_workbook_auto_from_rs(Cursor::new(bytes)).map_err(|e| CoreError::Import(format!("فایل اکسل قابل خواندن نیست: {e}")))?;
        let names = wb.sheet_names().to_vec();
        let sh = names.iter().find(|n| n.contains("دانش") || n.contains("آموز")).cloned().or_else(|| names.into_iter().next()).ok_or_else(|| CoreError::Import("شیت یافت نشد".into()))?;
        wb.worksheet_range(&sh).map_err(|e| CoreError::Import(e.to_string()))?.rows().map(|r| r.iter().map(cell_str).collect()).collect()
    } else {
        let txt = String::from_utf8(bytes.to_vec()).map_err(|_| CoreError::Import("فایل CSV باید UTF-8 باشد یا اکسل (.xlsx)".into()))?;
        let clean = txt.trim_start_matches('\u{FEFF}');
        let first = clean.lines().find(|l| !l.trim().is_empty()).ok_or_else(|| CoreError::Import("فایل خالی است".into()))?;
        let delim = if first.matches(';').count() > first.matches(',').count() { ';' } else if first.matches('\t').count() > first.matches(',').count() { '\t' } else { ',' };
        clean.lines().filter(|l| !l.trim().is_empty()).map(|l| parse_csv(l, delim)).collect()
    };
    if rows.is_empty() { return Err(CoreError::Import("فایل خالی است".into())); }

    let has_hdr = rows[0].iter().map(|c| normalize_persian(c)).any(|c| c.contains("ردیف") || c.contains("نام خانوادگی") || c.contains("کد ملی"));
    let mut parsed = Vec::with_capacity(rows.len());
    let mut skipped = 0i32;

    for (idx, cols) in rows[if has_hdr { 1 } else { 0 }..].iter().enumerate() {
        if cols.len() < 9 { skipped += 1; continue; }
        let row_num = normalize_persian(&cols[0]).parse::<i32>().unwrap_or((idx + 1) as i32);
        let school = { let s = cols[1].trim(); if s.is_empty() { "آموزشگاه".to_string() } else { s.to_string() } };
        let grade = cols[3].trim().to_string();
        let major = if is_middle_grade(&grade) { String::new() } else { cols[2].trim().to_string() };
        let sec = normalize_persian(&cols[4]).parse::<i32>().unwrap_or(1).max(1);
        let (f, l, fa) = (cols[5].trim().to_string(), cols[6].trim().to_string(), cols[7].trim().to_string());
        let nid = normalize_national_id(&cols[8]);
        let mob = cols.get(9).map(|m| normalize_mobile(m)).unwrap_or_default();
        if f.is_empty() || l.is_empty() || grade.is_empty() || nid.is_empty() { skipped += 1; continue; }
        let key = normalize_persian(&format!("{f} {l} {fa} {nid} {mob}"));
        parsed.push((row_num, school, major, grade, sec, f, l, fa, nid, mob, key));
    }
    if parsed.is_empty() { return Err(CoreError::Import("هیچ دانش‌آموز معتبری یافت نشد".into())); }

    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    if replace_existing { tx.execute("DELETE FROM students", []).map_err(|e| CoreError::Database(e.to_string()))?; }
    {
        let mut stmt = tx.prepare_cached(
            "INSERT INTO students (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, search_key)
             VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)
             ON CONFLICT(national_id) DO UPDATE SET
                 row_num=excluded.row_num, school_name=excluded.school_name, major=excluded.major, grade=excluded.grade,
                 section=excluded.section, first_name=excluded.first_name, last_name=excluded.last_name,
                 father_name=excluded.father_name, mobile=excluded.mobile, search_key=excluded.search_key",
        ).map_err(|e| CoreError::Database(e.to_string()))?;
        for r in &parsed {
            stmt.execute(params![r.0, r.1, r.2, r.3, r.4, r.5, r.6, r.7, r.8, r.9, r.10]).map_err(|e| CoreError::Database(e.to_string()))?;
        }
    }
    let classes: i32 = tx.query_row("SELECT COUNT(*) FROM (SELECT DISTINCT major, grade, section FROM students)", [], |r| r.get(0)).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(ImportReport { imported_count: parsed.len() as i32, skipped_count: skipped, classes_count: classes })
}

fn cell_str(c: &Data) -> String {
    match c {
        Data::String(s) => s.trim().to_string(),
        Data::Int(i) => i.to_string(),
        Data::Float(f) => if f.fract() == 0.0 { format!("{}", *f as i64) } else { f.to_string() },
        Data::Bool(b) => b.to_string(),
        Data::DateTime(dt) => dt.as_f64().to_string(),
        _ => String::new(),
    }
}

fn parse_csv(line: &str, delim: char) -> Vec<String> {
    let (mut out, mut cur, mut q) = (Vec::with_capacity(10), String::new(), false);
    let mut it = line.chars().peekable();
    while let Some(c) = it.next() {
        if q {
            if c == '"' { if it.peek() == Some(&'"') { it.next(); cur.push('"'); } else { q = false; } } else { cur.push(c); }
        } else if c == '"' { q = true; } else if c == delim { out.push(cur.trim().to_string()); cur.clear(); } else { cur.push(c); }
    }
    out.push(cur.trim().to_string());
    out
}
''',

    "rust-core/src/db.rs": r'''use crate::models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    GradeCategory, ImportReport, MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary,
    SavedContact, StudentAttendanceRow, StudentGradeRow, StudentMonthlyEvent, TopStudentCount,
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
             id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, sort_order INTEGER NOT NULL DEFAULT 0
         );

         CREATE TABLE IF NOT EXISTS student_grades (
             student_id INTEGER NOT NULL, category_id INTEGER NOT NULL,
             score TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', updated_at INTEGER NOT NULL,
             PRIMARY KEY (student_id, category_id),
             FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
             FOREIGN KEY (category_id) REFERENCES grade_categories(id) ON DELETE CASCADE
         );

         CREATE TABLE IF NOT EXISTS saved_contacts (
             id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, role TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL UNIQUE
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
            current_status: cur, period_statuses: sts, event_time: r.get(11)?, note: r.get(12)?, latest_grade: r.get(13)?,
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

pub fn set_attendance(conn: &mut Connection, student_id: i64, date_iso: &str, period: Period, status: AttendanceStatus, event_time: &str, note: &str, teacher: &str, lesson: &str, class_time: &str) -> Result<(), CoreError> {
    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    let now = now_unix();
    let pn = period.to_i32();
    let clean_time = if matches!(status, AttendanceStatus::LeftClass | AttendanceStatus::Late) { event_time.trim() } else { "" };

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
        params![student_id, date_iso, pn, status.to_i32(), clean_time, note.trim(), teacher.trim(), lesson.trim(), class_time.trim(), now],
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

pub fn get_grade_categories(conn: &Connection) -> Result<Vec<GradeCategory>, CoreError> {
    let mut st = conn.prepare_cached("SELECT id, name FROM grade_categories ORDER BY sort_order ASC, id ASC").map_err(|e| CoreError::Database(e.to_string()))?;
    let rows = st.query_map([], |r| Ok(GradeCategory { id: r.get(0)?, name: r.get(1)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(rows)
}

pub fn add_grade_category(conn: &Connection, name: &str) -> Result<i64, CoreError> {
    let n = name.trim();
    if n.is_empty() { return Err(CoreError::InvalidInput("عنوان نمره را وارد کنید".into())); }
    let next_order: i32 = conn.query_row("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM grade_categories", [], |r| r.get(0)).unwrap_or(10);
    conn.execute("INSERT INTO grade_categories (name, sort_order) VALUES (?1, ?2)", params![n, next_order])
        .map_err(|e| if e.to_string().contains("UNIQUE") { CoreError::InvalidInput("این عنوان قبلاً وجود دارد".into()) } else { CoreError::Database(e.to_string()) })?;
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

pub fn get_saved_contacts(conn: &Connection) -> Result<Vec<SavedContact>, CoreError> {
    let mut st = conn.prepare_cached("SELECT id, name, role, phone FROM saved_contacts ORDER BY id ASC").map_err(|e| CoreError::Database(e.to_string()))?;
    let rows = st.query_map([], |r| Ok(SavedContact { id: r.get(0)?, name: r.get(1)?, role: r.get(2)?, phone: r.get(3)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|e| CoreError::Database(e.to_string()))?;
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
    let s_rows = ss.query_map(params![major, grade, section], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, String>(2)?)))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    for (id, f, l) in s_rows { names.insert(id, format!("{f} {l}")); }

    let mut ast = conn.prepare_cached("SELECT a.student_id, a.date_iso, a.period, a.status FROM attendance a INNER JOIN students s ON s.id=a.student_id WHERE s.major=?1 AND s.grade=?2 AND s.section=?3 AND a.status!=0").map_err(|e| CoreError::Database(e.to_string()))?;
    let a_rows = ast.query_map(params![major, grade, section], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?))))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut sessions = HashSet::new();
    let (mut ta, mut tl, mut te, mut tlc) = (0, 0, 0, 0);
    let (mut ma, mut ml, mut me, mut mlc): (HashMap<i64, i32>, HashMap<i64, i32>, HashMap<i64, i32>, HashMap<i64, i32>) = Default::default();
    for (sid, d, p, st) in a_rows {
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

pub fn get_student_monthly_details(conn: &Connection, student_id: i64, jy: i32, jm_i: i32) -> Result<Vec<StudentMonthlyEvent>, CoreError> {
    let jm = jm_i.clamp(1, 12) as u32;
    let (s_iso, e_iso) = jalali_month_range_iso(jy, jm);
    let mut st = conn.prepare_cached(
        "SELECT date_iso, period, status, exit_time, note
         FROM attendance
         WHERE student_id=?1 AND date_iso>=?2 AND date_iso<=?3 AND status IN (2,3,4,5)
         ORDER BY date_iso DESC, period ASC",
    ).map_err(|e| CoreError::Database(e.to_string()))?;

    let rows = st.query_map(params![student_id, s_iso, e_iso], |r| {
        let date_iso: String = r.get(0)?;
        let period = Period::from_i32(r.get(1)?);
        let status = AttendanceStatus::from_i32(r.get(2)?);
        Ok(StudentMonthlyEvent {
            jalali_date: format_iso_to_jalali(&date_iso),
            date_iso, period_label: period.label_fa().to_string(),
            status, event_time: r.get(3)?, note: r.get(4)?,
        })
    }).map_err(|e| CoreError::Database(e.to_string()))?
      .collect::<Result<Vec<_>, _>>()
      .map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(rows)
}

pub fn get_monthly_report(conn: &Connection, major: &str, grade: &str, section: i32, jy: i32, jm_i: i32) -> Result<MonthlyClassReport, CoreError> {
    let jm = jm_i.clamp(1, 12) as u32;
    let (s_iso, e_iso) = jalali_month_range_iso(jy, jm);
    let mut ss = conn.prepare_cached("SELECT id, first_name, last_name, father_name, national_id, mobile FROM students WHERE major=?1 AND grade=?2 AND section=?3").map_err(|e| CoreError::Database(e.to_string()))?;
    let mut base: Vec<(i64, String, String, String, String, String)> = ss.query_map(params![major, grade, section], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?, r.get(3)?, r.get(4)?, r.get(5)?)))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    base.sort_by(|a, b| persian_sort_key(&a.2).cmp(&persian_sort_key(&b.2)).then_with(|| persian_sort_key(&a.1).cmp(&persian_sort_key(&b.1))));

    let mut ast = conn.prepare_cached("SELECT a.student_id, a.date_iso, a.period, a.status FROM attendance a INNER JOIN students s ON s.id=a.student_id WHERE s.major=?1 AND s.grade=?2 AND s.section=?3 AND a.date_iso>=?4 AND a.date_iso<=?5 AND a.status!=0").map_err(|e| CoreError::Database(e.to_string()))?;
    let a_rows = ast.query_map(params![major, grade, section, s_iso, e_iso], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?, r.get::<_, i32>(2)?, AttendanceStatus::from_i32(r.get::<_, i32>(3)?))))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let (mut active_d, mut stu_d): (HashMap<String, HashSet<i32>>, HashMap<(i64, String), HashMap<i32, AttendanceStatus>>) = Default::default();
    for (sid, d, p, st) in a_rows {
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
    let mut st1 = conn.prepare("SELECT row_num,school_name,major,grade,section,first_name,last_name,father_name,national_id,mobile FROM students").map_err(|e| CoreError::Database(e.to_string()))?;
    let students: Vec<BkStu> = st1.query_map([], |r| Ok(BkStu { row_num: r.get(0)?, school_name: r.get(1)?, major: r.get(2)?, grade: r.get(3)?, section: r.get(4)?, first_name: r.get(5)?, last_name: r.get(6)?, father_name: r.get(7)?, national_id: r.get(8)?, mobile: r.get(9)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut st2 = conn.prepare("SELECT s.national_id,a.date_iso,a.period,a.status,a.exit_time,a.note,a.teacher_name,a.lesson_name,a.class_time FROM attendance a INNER JOIN students s ON s.id=a.student_id").map_err(|e| CoreError::Database(e.to_string()))?;
    let attendance: Vec<BkAtt> = st2.query_map([], |r| Ok(BkAtt { national_id: r.get(0)?, date_iso: r.get(1)?, period: r.get(2)?, status: r.get(3)?, exit_time: r.get(4)?, note: r.get(5)?, teacher_name: r.get(6)?, lesson_name: r.get(7)?, class_time: r.get(8)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut st3 = conn.prepare("SELECT name FROM grade_categories ORDER BY sort_order ASC, id ASC").map_err(|e| CoreError::Database(e.to_string()))?;
    let grade_categories: Vec<String> = st3.query_map([], |r| r.get(0))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut st4 = conn.prepare("SELECT s.national_id,c.name,g.score,g.note FROM student_grades g INNER JOIN students s ON s.id=g.student_id INNER JOIN grade_categories c ON c.id=g.category_id WHERE g.score!='' OR g.note!=''").map_err(|e| CoreError::Database(e.to_string()))?;
    let grades: Vec<BkGrade> = st4.query_map([], |r| Ok(BkGrade { national_id: r.get(0)?, category_name: r.get(1)?, score: r.get(2)?, note: r.get(3)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut st5 = conn.prepare("SELECT name,role,phone FROM saved_contacts").map_err(|e| CoreError::Database(e.to_string()))?;
    let contacts: Vec<BkContact> = st5.query_map([], |r| Ok(BkContact { name: r.get(0)?, role: r.get(1)?, phone: r.get(2)? }))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;

    let mut st6 = conn.prepare("SELECT key,value FROM app_settings").map_err(|e| CoreError::Database(e.to_string()))?;
    let set_rows = st6.query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))
        .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
    let mut settings = HashMap::new();
    for (k, v) in set_rows { settings.insert(k, v); }

    serde_json::to_string_pretty(&BkPayload { version: 5, students, attendance, grade_categories, grades, contacts, settings }).map_err(|e| CoreError::Import(e.to_string()))
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
        let c_rows = cst.query_map([], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, String>(1)?)))
            .map_err(|e| CoreError::Database(e.to_string()))?.collect::<Result<Vec<_>, _>>().map_err(|e| CoreError::Database(e.to_string()))?;
        for (id, n) in c_rows { cat_map.insert(n, id); }
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
''',

    "rust-core/src/reports.rs": r'''use crate::db;
use crate::models::{AttendanceStatus, ClassGroup, CoreError, MonthlyClassReport, Period, PrincipalReportBundle};
use crate::persian::{format_iso_to_jalali, format_iso_to_jalali_short, to_persian_digits};
use rusqlite::Connection;
use rust_xlsxwriter::{Color, Format, FormatAlign, Workbook};
use std::collections::{HashMap, HashSet};

const P_FULL: [&str; 4] = ["زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
const P_SMS: [&str; 4] = ["زنگ ۱", "زنگ ۲", "زنگ ۳", "زنگ ۴"];

fn cls_title(major: &str, grade: &str, sec: i32, show_section: bool) -> String {
    let s = to_persian_digits(&sec.to_string());
    match (major.trim().is_empty(), show_section) {
        (true, true) => format!("پایه {grade} شعبه {s}"),
        (true, false) => format!("پایه {grade}"),
        (false, true) => format!("{major} - {grade} شعبه {s}"),
        (false, false) => format!("{major} - {grade}"),
    }
}

fn build_multi_section_map(all: &[ClassGroup]) -> HashMap<(String, String), bool> {
    let mut sets: HashMap<(String, String), HashSet<i32>> = HashMap::new();
    for c in all { sets.entry((c.major.clone(), c.grade.clone())).or_default().insert(c.section); }
    sets.into_iter().map(|(k, v)| (k, v.len() > 1)).collect()
}

/// نمایش تأخیر بر اساس دقیقه (مثلاً: «تأخیر ۱۰ دقیقه») و پشتیبانی از رکوردهای قدیمی ساعتی
fn late_suffix(val: &str, note: &str) -> String {
    let clean = val.trim();
    let t = to_persian_digits(clean);
    let base = if t.is_empty() {
        "تأخیر".to_string()
    } else if clean.contains(':') {
        format!("تأخیر ساعت {t}")
    } else {
        format!("تأخیر {t} دقیقه")
    };
    if note.trim().is_empty() { base } else { format!("{base} - {}", note.trim()) }
}

fn exit_suffix(time: &str, note: &str) -> String {
    let t = to_persian_digits(time.trim());
    match (t.is_empty(), note.trim().is_empty()) {
        (true, true) => "خروج از کلاس".into(),
        (false, true) => format!("خروج ساعت {t}"),
        (true, false) => format!("خروج - {}", note.trim()),
        (false, false) => format!("خروج ساعت {t} - {}", note.trim()),
    }
}

pub fn generate_period_group_message(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, period: Period, target: AttendanceStatus, teacher: &str, lesson: &str, whole: bool) -> Result<String, CoreError> {
    let all = db::get_classes(conn)?;
    let multi = build_multi_section_map(&all);
    let classes: Vec<ClassGroup> = if whole { all } else { all.into_iter().filter(|c| c.major == major && c.grade == grade && c.section == section).collect() };
    if classes.is_empty() { return Err(CoreError::InvalidInput("هیچ کلاسی یافت نشد".into())); }

    let (action, empty_w) = match target {
        AttendanceStatus::Late => ("با تأخیر حاضر شده‌اند", "تأخیری"),
        AttendanceStatus::LeftClass => ("پس از حضور از کلاس خارج شده و بازنگشته‌اند", "خروج از کلاسی"),
        _ => ("غایب بوده‌اند", "غایبی"),
    };
    let jalali = format_iso_to_jalali_short(date_iso);
    let lp = if lesson.trim().is_empty() { String::new() } else { format!("در درس {} ", lesson.trim()) };
    let school = &classes[0].school_name;
    let mut body = String::new();
    let mut cnt = 0usize;

    for cls in &classes {
        let snap = db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, period, "")?;
        let m: Vec<_> = snap.students.into_iter().filter(|s| s.current_status == target).collect();
        if m.is_empty() { continue; }
        let show_sec = *multi.get(&(cls.major.clone(), cls.grade.clone())).unwrap_or(&false);
        if whole { body.push_str(&format!("\n[{}]\n", cls_title(&cls.major, &cls.grade, cls.section, show_sec))); }
        for (i, s) in m.iter().enumerate() {
            cnt += 1;
            let num = to_persian_digits(&(i + 1).to_string());
            let fa = if s.father_name.is_empty() { "ثبت نشده" } else { &s.father_name };
            let tag = match target {
                AttendanceStatus::Late => late_suffix(&s.event_time, &s.note),
                AttendanceStatus::LeftClass => exit_suffix(&s.event_time, &s.note),
                _ => "غایب".into(),
            };
            body.push_str(&format!("{num}. {} {}، فرزند {fa} ({tag})\n", s.first_name, s.last_name));
        }
    }
    if cnt == 0 { return Err(CoreError::InvalidInput(format!("در {} هیچ دانش‌آموز {empty_w} ثبت نشده است", period.label_fa()))); }
    let show_sec_cur = *multi.get(&(major.to_string(), grade.to_string())).unwrap_or(&false);
    let scope = if whole { format!("کل {school}") } else { cls_title(major, grade, section, show_sec_cur) };
    let mut msg = format!("سلام علیکم\nمدیریت محترم {school}،\nدانش‌آموزان زیر {lp}{scope}، {} مورخه {jalali} {action}:\n\n{}", period.label_fa(), body.trim());
    if !teacher.trim().is_empty() { msg.push_str(&format!("\n\nبا تشکر\n{}", teacher.trim())); }
    Ok(msg)
}

pub fn generate_principal_report(conn: &Connection, major: Option<&str>, grade: Option<&str>, section: Option<i32>, date_iso: &str, teacher: &str) -> Result<PrincipalReportBundle, CoreError> {
    let all = db::get_classes(conn)?;
    let multi = build_multi_section_map(&all);
    let classes: Vec<ClassGroup> = match (major, grade, section) {
        (Some(m), Some(g), Some(sec)) => all.into_iter().filter(|c| c.major == m && c.grade == g && c.section == sec).collect(),
        _ => all,
    };
    if classes.is_empty() { return Err(CoreError::InvalidInput("هیچ کلاسی یافت نشد".into())); }

    let jf = format_iso_to_jalali(date_iso);
    let js = format_iso_to_jalali_short(date_iso);
    let school = &classes[0].school_name;
    let is_whole = classes.len() > 1;

    let mut full = format!("📋 گزارش حضور و غیاب {school}\n📅 تاریخ: {jf}\n");
    if !teacher.trim().is_empty() { full.push_str(&format!("👤 دبیر: {}\n", teacher.trim())); }
    let mut sms = if is_whole { format!("گزارش {school} ({js})\n") } else {
        let c = &classes[0];
        let show_sec = *multi.get(&(c.major.clone(), c.grade.clone())).unwrap_or(&false);
        let t = cls_title(&c.major, &c.grade, c.section, show_sec);
        full.push_str(&format!("🏫 کلاس: {t}\n"));
        format!("گزارش {t} ({js})\n")
    };

    let (mut tfd, mut tpa, mut tla, mut tlc) = (0, 0, 0, 0);
    let mut any_data = false;

    for cls in &classes {
        let snaps = [
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?,
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::Second, "")?,
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::Third, "")?,
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::Fourth, "")?,
        ];
        let active: Vec<usize> = (0..4).filter(|&p| snaps[p].is_period_saved).collect();
        if active.is_empty() { continue; }
        any_data = true;

        let mut fd_ids = HashSet::new();
        let (mut fd_full, mut fd_sms) = (Vec::new(), Vec::new());
        if active.len() >= 2 {
            for s in &snaps[0].students {
                if active.iter().all(|&p| matches!(s.period_statuses[p], AttendanceStatus::Absent | AttendanceStatus::Excused)) {
                    fd_ids.insert(s.student_id);
                    let tag = if active.iter().all(|&p| s.period_statuses[p] == AttendanceStatus::Excused) { "غیبت موجه" } else { "غایب" };
                    fd_full.push(format!("{} {} ({tag})", s.first_name, s.last_name));
                    fd_sms.push(format!("{} {}({tag})", s.first_name, s.last_name));
                }
            }
        }

        let mut per_p = Vec::new();
        let mut has_issue = !fd_full.is_empty();
        for &p in &active {
            let (mut fi, mut si, mut pcnt) = (Vec::new(), Vec::new(), 0i32);
            for s in &snaps[p].students {
                let st = s.period_statuses[p];
                if matches!(st, AttendanceStatus::Present | AttendanceStatus::Unmarked) { pcnt += 1; }
                if fd_ids.contains(&s.student_id) { continue; }
                match st {
                    AttendanceStatus::Absent => { tpa += 1; has_issue = true; fi.push(format!("{} {} (غایب)", s.first_name, s.last_name)); si.push(format!("{} {}(غایب)", s.first_name, s.last_name)); }
                    AttendanceStatus::Excused => { tpa += 1; has_issue = true; fi.push(format!("{} {} (غیبت موجه)", s.first_name, s.last_name)); si.push(format!("{} {}(غیبت موجه)", s.first_name, s.last_name)); }
                    AttendanceStatus::Late => {
                        tla += 1; has_issue = true;
                        let lt = late_suffix(&s.event_time, &s.note);
                        fi.push(format!("{} {} ({lt})", s.first_name, s.last_name));
                        si.push(format!("{} {}({lt})", s.first_name, s.last_name));
                    }
                    AttendanceStatus::LeftClass => {
                        tlc += 1; has_issue = true;
                        let ex = exit_suffix(&s.event_time, &s.note);
                        fi.push(format!("{} {} ({ex})", s.first_name, s.last_name));
                        si.push(format!("{} {}({ex})", s.first_name, s.last_name));
                    }
                    _ => {}
                }
            }
            per_p.push((p, pcnt, fi, si));
        }
        tfd += fd_full.len() as i32;

        if is_whole {
            if !has_issue { continue; }
            let show_sec = *multi.get(&(cls.major.clone(), cls.grade.clone())).unwrap_or(&false);
            let h = cls_title(&cls.major, &cls.grade, cls.section, show_sec);
            full.push_str(&format!("\n────────────\n🏫 {h}\n"));
            sms.push_str(&format!("\n[{h}]\n"));
        } else { full.push_str("────────────────────\n"); }

        if !has_issue {
            let n = to_persian_digits(&snaps[0].students.len().to_string());
            full.push_str(&format!("✅ همه {n} دانش‌آموز حاضر بودند.\n"));
            sms.push_str(&format!("وضعیت: همه {n} نفر حاضر\n"));
            continue;
        }
        if !fd_full.is_empty() {
            full.push_str(&format!("🔴 غایبین کل روز ({} نفر):\n", to_persian_digits(&fd_full.len().to_string())));
            for x in &fd_full { full.push_str(&format!("• {x}\n")); }
            sms.push_str(&format!("غایب کل روز: {}\n", fd_sms.join("، ")));
        }
        for (p, pcnt, fi, si) in per_p {
            let pf = to_persian_digits(&pcnt.to_string());
            if fi.is_empty() {
                if !is_whole {
                    full.push_str(&format!("\n🔔 {} ({pf} حاضر):\n• بقیه همه حاضر بودند\n", P_FULL[p]));
                    sms.push_str(&format!("{}: بقیه حاضر ({pf} نفر)\n", P_SMS[p]));
                }
            } else {
                full.push_str(&format!("\n🔔 {} ({pf} حاضر):\n", P_FULL[p]));
                for x in &fi { full.push_str(&format!("• {x}\n")); }
                sms.push_str(&format!("{}: {} | {pf} حاضر\n", P_SMS[p], si.join("، ")));
            }
        }
    }

    if !any_data {
        full.push_str("\nهنوز تغییری ثبت نشده است (پیش‌فرض همه حاضر).");
        sms.push_str("وضعیت: همه حاضر");
    } else if is_whole && tfd == 0 && tpa == 0 && tla == 0 && tlc == 0 {
        full.push_str("\n✅ امروز در همه کلاس‌های ثبت‌شده همه دانش‌آموزان حاضر بودند.");
        sms.push_str("وضعیت کل: همه حاضر");
    }
    Ok(PrincipalReportBundle { full_text: full.trim().into(), sms_text: sms.trim().into(), full_day_absent_count: tfd, partial_absent_count: tpa, late_count: tla, left_class_count: tlc })
}

pub fn export_daily_csv(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str) -> Result<String, CoreError> {
    let snap = db::get_class_attendance(conn, major, grade, section, date_iso, Period::First, "")?;
    let mut csv = String::with_capacity(snap.students.len() * 140 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل,تاریخ,زنگ اول,زنگ دوم,زنگ سوم,زنگ چهارم\n");
    for (i, s) in snap.students.iter().enumerate() {
        csv.push_str(&format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
            i + 1, major, grade, section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, snap.jalali_date,
            s.period_statuses[0].label_fa(), s.period_statuses[1].label_fa(), s.period_statuses[2].label_fa(), s.period_statuses[3].label_fa()));
    }
    Ok(csv)
}

pub fn export_daily_xlsx(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, all_classes: bool) -> Result<Vec<u8>, CoreError> {
    let all = db::get_classes(conn)?;
    let multi = build_multi_section_map(&all);
    let classes: Vec<ClassGroup> = if all_classes { all } else { all.into_iter().filter(|c| c.major == major && c.grade == grade && c.section == section).collect() };
    if classes.is_empty() { return Err(CoreError::InvalidInput("کلاسی برای خروجی نیست".into())); }

    let mut wb = Workbook::new();
    let hf = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x1B5E20)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cf = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    let pf = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xD7F5E6)).set_font_color(Color::RGB(0x1B5E20)).set_align(FormatAlign::Center);
    let af = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFDADF)).set_font_color(Color::RGB(0xB71C1C)).set_align(FormatAlign::Center);
    let lf = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFECC7)).set_font_color(Color::RGB(0x9A5B00)).set_align(FormatAlign::Center);
    let ef = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xDCE7FF)).set_font_color(Color::RGB(0x1A47A6)).set_align(FormatAlign::Center);
    let lcf = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xF3E8FF)).set_font_color(Color::RGB(0x6B21A8)).set_align(FormatAlign::Center);

    let hdrs = ["ردیف", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل", "تاریخ", "زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
    let mut used = HashSet::new();
    for cls in classes {
        let snaps = [
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?,
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::Second, "")?,
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::Third, "")?,
            db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::Fourth, "")?,
        ];
        let sh = wb.add_worksheet();
        let show_sec = *multi.get(&(cls.major.clone(), cls.grade.clone())).unwrap_or(&false);
        sh.set_name(&unique_name(&cls_title(&cls.major, &cls.grade, cls.section, show_sec), &mut used)).map_err(|e| CoreError::Import(e.to_string()))?;
        sh.set_right_to_left(true);
        for (c, h) in hdrs.iter().enumerate() { let _ = sh.write_string_with_format(0, c as u16, *h, &hf); }
        for (idx, s) in snaps[0].students.iter().enumerate() {
            let r = (idx + 1) as u32;
            let _ = sh.write_number_with_format(r, 0, (idx + 1) as f64, &cf);
            let _ = sh.write_string_with_format(r, 1, &s.first_name, &cf);
            let _ = sh.write_string_with_format(r, 2, &s.last_name, &cf);
            let _ = sh.write_string_with_format(r, 3, &s.father_name, &cf);
            let _ = sh.write_string_with_format(r, 4, &s.national_id, &cf);
            let _ = sh.write_string_with_format(r, 5, &s.mobile, &cf);
            let _ = sh.write_string_with_format(r, 6, &snaps[0].jalali_date, &cf);
            for p in 0..4 {
                let row_p = &snaps[p].students[idx];
                let st = s.period_statuses[p];
                let (txt, fmt) = match st {
                    AttendanceStatus::Absent => ("غایب".to_string(), &af),
                    AttendanceStatus::Late => (late_suffix(&row_p.event_time, &row_p.note), &lf),
                    AttendanceStatus::Excused => ("غیبت موجه".to_string(), &ef),
                    AttendanceStatus::LeftClass => (exit_suffix(&row_p.event_time, &row_p.note), &lcf),
                    _ => ("حاضر".to_string(), &pf),
                };
                let _ = sh.write_string_with_format(r, (7 + p) as u16, &txt, fmt);
            }
        }
        sh.autofit();
    }
    wb.save_to_buffer().map_err(|e| CoreError::Import(e.to_string()))
}

pub fn export_gradebook_xlsx(conn: &Connection, major: &str, grade: &str, section: i32) -> Result<Vec<u8>, CoreError> {
    let cats = db::get_grade_categories(conn)?;
    let snap = db::get_class_attendance(conn, major, grade, section, "2025-10-12", Period::First, "")?;
    let mut score_map: HashMap<(i64, i64), String> = HashMap::new();
    for c in &cats {
        for r in db::get_class_grades(conn, major, grade, section, c.id)? {
            if !r.score.is_empty() { score_map.insert((r.student_id, c.id), r.score); }
        }
    }
    let mut wb = Workbook::new();
    let sh = wb.add_worksheet();
    let mut used = HashSet::new();
    sh.set_name(&unique_name(&format!("نمرات {} {}", grade, section), &mut used)).map_err(|e| CoreError::Import(e.to_string()))?;
    sh.set_right_to_left(true);
    let hf = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x4C1D95)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cf = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    for (c, h) in ["ردیف", "نام", "نام خانوادگی", "نام پدر"].iter().enumerate() { let _ = sh.write_string_with_format(0, c as u16, *h, &hf); }
    for (ci, cat) in cats.iter().enumerate() { let _ = sh.write_string_with_format(0, (4 + ci) as u16, &cat.name, &hf); }
    for (idx, s) in snap.students.iter().enumerate() {
        let r = (idx + 1) as u32;
        let _ = sh.write_number_with_format(r, 0, (idx + 1) as f64, &cf);
        let _ = sh.write_string_with_format(r, 1, &s.first_name, &cf);
        let _ = sh.write_string_with_format(r, 2, &s.last_name, &cf);
        let _ = sh.write_string_with_format(r, 3, &s.father_name, &cf);
        for (ci, cat) in cats.iter().enumerate() {
            if let Some(sc) = score_map.get(&(s.student_id, cat.id)) { let _ = sh.write_string_with_format(r, (4 + ci) as u16, sc, &cf); }
        }
    }
    sh.autofit();
    wb.save_to_buffer().map_err(|e| CoreError::Import(e.to_string()))
}

pub fn export_monthly_xlsx(rep: &MonthlyClassReport, major: &str, grade: &str, sec: i32, show_sec: bool) -> Result<Vec<u8>, CoreError> {
    let mut wb = Workbook::new();
    let sh = wb.add_worksheet();
    let mut used = HashSet::new();
    sh.set_name(&unique_name(&format!("ماهانه {}", rep.month_label), &mut used)).map_err(|e| CoreError::Import(e.to_string()))?;
    sh.set_right_to_left(true);
    let hf = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x0D47A1)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cf = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    for (c, h) in ["ردیف", "کلاس", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "حاضر", "غایب", "کل روز", "تأخیر", "غیبت موجه", "خروج", "درصد"].iter().enumerate() {
        let _ = sh.write_string_with_format(0, c as u16, *h, &hf);
    }
    let cl = cls_title(major, grade, sec, show_sec);
    for (i, s) in rep.students.iter().enumerate() {
        let r = (i + 1) as u32;
        let _ = sh.write_number_with_format(r, 0, (i + 1) as f64, &cf);
        let _ = sh.write_string_with_format(r, 1, &cl, &cf);
        let _ = sh.write_string_with_format(r, 2, &s.first_name, &cf);
        let _ = sh.write_string_with_format(r, 3, &s.last_name, &cf);
        let _ = sh.write_string_with_format(r, 4, &s.father_name, &cf);
        let _ = sh.write_string_with_format(r, 5, &s.national_id, &cf);
        let _ = sh.write_number_with_format(r, 6, s.present_periods as f64, &cf);
        let _ = sh.write_number_with_format(r, 7, s.absent_periods as f64, &cf);
        let _ = sh.write_number_with_format(r, 8, s.full_absent_days as f64, &cf);
        let _ = sh.write_number_with_format(r, 9, s.late_periods as f64, &cf);
        let _ = sh.write_number_with_format(r, 10, s.excused_periods as f64, &cf);
        let _ = sh.write_number_with_format(r, 11, s.left_class_periods as f64, &cf);
        let _ = sh.write_string_with_format(r, 12, &format!("{}٪", to_persian_digits(&format!("{:.1}", s.attendance_percent))), &cf);
    }
    sh.autofit();
    wb.save_to_buffer().map_err(|e| CoreError::Import(e.to_string()))
}

pub fn export_monthly_csv(rep: &MonthlyClassReport, major: &str, grade: &str, sec: i32) -> String {
    let mut csv = String::from("\u{FEFF}ردیف,ماه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,حاضر,غایب,کل روز,تأخیر,غیبت موجه,خروج,درصد حضور\n");
    for (i, s) in rep.students.iter().enumerate() {
        csv.push_str(&format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.1}%\n",
            i + 1, rep.month_label, major, grade, sec, s.first_name, s.last_name, s.father_name, s.national_id,
            s.present_periods, s.absent_periods, s.full_absent_days, s.late_periods, s.excused_periods, s.left_class_periods, s.attendance_percent));
    }
    csv
}

pub fn export_template_xlsx() -> Result<Vec<u8>, CoreError> {
    let mut wb = Workbook::new();
    let sh = wb.add_worksheet();
    sh.set_name("دانش‌آموزان").map_err(|e| CoreError::Import(e.to_string()))?;
    sh.set_right_to_left(true);
    let hf = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x145548)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cf = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    for (c, h) in ["ردیف", "نام مدرسه", "رشته", "پایه", "شعبه", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل"].iter().enumerate() { let _ = sh.write_string_with_format(0, c as u16, *h, &hf); }
    for (ri, row) in [
        ["1", "آموزشگاه نمونه", "صنایع شیمیایی", "دهم", "1", "علی", "احمدی", "حسن", "1000000001", "09121234561"],
        ["2", "آموزشگاه نمونه", "الکتروتکنیک", "یازدهم", "1", "رضا", "محمدی", "مهدی", "1000000002", "09121234562"],
    ].iter().enumerate() {
        for (ci, v) in row.iter().enumerate() { let _ = sh.write_string_with_format((ri + 1) as u32, ci as u16, *v, &cf); }
    }
    sh.autofit();
    wb.save_to_buffer().map_err(|e| CoreError::Import(e.to_string()))
}

fn unique_name(raw: &str, used: &mut HashSet<String>) -> String {
    let clean: String = raw.chars().filter(|c| !matches!(c, ':' | '\\' | '/' | '?' | '*' | '[' | ']')).collect();
    let mut b: String = clean.chars().take(28).collect();
    if b.trim().is_empty() { b = "Sheet".into(); }
    if used.insert(b.clone()) { return b; }
    for n in 2..99 { let c = format!("{}_{}", b.chars().take(25).collect::<String>(), n); if used.insert(c.clone()) { return c; } }
    "Sheet_X".into()
}
''',

    "rust-core/src/lib.rs": r'''mod db;
mod importer;
mod models;
mod persian;
mod reports;

pub use models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    GradeCategory, ImportReport, JalaliDayCell, JalaliMonthGrid, JalaliYearMonth,
    MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary, PrincipalReportBundle,
    SavedContact, StudentAttendanceRow, StudentGradeRow, StudentMonthlyEvent, TopStudentCount,
};

use rusqlite::Connection;
use std::sync::{Arc, Mutex};

uniffi::setup_scaffolding!();

#[derive(uniffi::Object)]
pub struct AttendanceEngine { conn: Mutex<Connection> }

#[uniffi::export]
impl AttendanceEngine {
    #[uniffi::constructor]
    pub fn new(db_path: String) -> Result<Arc<Self>, CoreError> {
        Ok(Arc::new(Self { conn: Mutex::new(db::init_database(&db_path)?) }))
    }

    pub fn import_file_bytes(&self, file_name: String, bytes: Vec<u8>, replace_existing: bool) -> Result<ImportReport, CoreError> {
        let mut c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        importer::import_file_bytes(&mut *c, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_classes(&*c)
    }

    pub fn get_class_attendance(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, search_query: String) -> Result<ClassAttendanceSnapshot, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_attendance(&*c, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(&self, student_id: i64, date_iso: String, period: Period, status: AttendanceStatus, event_time: String, note: String, teacher_name: String, lesson_name: String, class_time: String) -> Result<(), CoreError> {
        let mut c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_attendance(&mut *c, student_id, &date_iso, period, status, &event_time, &note, &teacher_name, &lesson_name, &class_time)
    }

    pub fn mark_class_status(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher_name: String, lesson_name: String, class_time: String) -> Result<i32, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::mark_class_status(&*c, &major, &grade, section, &date_iso, period, status, only_unmarked, &teacher_name, &lesson_name, &class_time)
    }

    pub fn copy_from_previous_period(&self, major: String, grade: String, section: i32, date_iso: String, target_period: Period) -> Result<i32, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::copy_from_previous_period(&*c, &major, &grade, section, &date_iso, target_period)
    }

    pub fn add_student(&self, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<i64, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::add_student(&*c, &school_name, &major, &grade, section, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn update_student(&self, student_id: i64, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<(), CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::update_student(&*c, student_id, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn delete_student(&self, student_id: i64) -> Result<(), CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_student(&*c, student_id)
    }

    pub fn delete_class(&self, major: String, grade: String, section: i32) -> Result<i32, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_class(&*c, &major, &grade, section)
    }

    pub fn get_grade_categories(&self) -> Result<Vec<GradeCategory>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_grade_categories(&*c)
    }

    pub fn add_grade_category(&self, name: String) -> Result<i64, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::add_grade_category(&*c, &name)
    }

    pub fn delete_grade_category(&self, category_id: i64) -> Result<(), CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_grade_category(&*c, category_id)
    }

    pub fn get_class_grades(&self, major: String, grade: String, section: i32, category_id: i64) -> Result<Vec<StudentGradeRow>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_grades(&*c, &major, &grade, section, category_id)
    }

    pub fn set_student_grade(&self, student_id: i64, category_id: i64, score: String, note: String) -> Result<(), CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_student_grade(&*c, student_id, category_id, &score, &note)
    }

    pub fn export_gradebook_xlsx(&self, major: String, grade: String, section: i32) -> Result<Vec<u8>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_gradebook_xlsx(&*c, &major, &grade, section)
    }

    pub fn get_saved_contacts(&self) -> Result<Vec<SavedContact>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_saved_contacts(&*c)
    }

    pub fn save_contact(&self, name: String, role: String, phone: String) -> Result<i64, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::save_contact(&*c, &name, &role, &phone)
    }

    pub fn delete_contact(&self, contact_id: i64) -> Result<(), CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_contact(&*c, contact_id)
    }

    pub fn get_backup_stats(&self) -> Result<BackupStats, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_backup_stats(&*c)
    }

    pub fn get_class_analytics(&self, major: String, grade: String, section: i32) -> Result<ClassAnalytics, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_analytics(&*c, &major, &grade, section)
    }

    pub fn get_student_monthly_details(&self, student_id: i64, jalali_year: i32, jalali_month: i32) -> Result<Vec<StudentMonthlyEvent>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_student_monthly_details(&*c, student_id, jalali_year, jalali_month)
    }

    pub fn generate_period_group_message(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, target_status: AttendanceStatus, teacher_name: String, lesson_name: String, whole_school: bool) -> Result<String, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::generate_period_group_message(&*c, &major, &grade, section, &date_iso, period, target_status, &teacher_name, &lesson_name, whole_school)
    }

    pub fn generate_principal_report(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool, teacher_name: String) -> Result<PrincipalReportBundle, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        if whole_school { reports::generate_principal_report(&*c, None, None, None, &date_iso, &teacher_name) }
        else { reports::generate_principal_report(&*c, Some(&major), Some(&grade), Some(section), &date_iso, &teacher_name) }
    }

    pub fn export_daily_csv(&self, major: String, grade: String, section: i32, date_iso: String) -> Result<String, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_daily_csv(&*c, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool) -> Result<Vec<u8>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_daily_xlsx(&*c, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn get_monthly_report(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_monthly_report(&*c, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<Vec<u8>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let r = db::get_monthly_report(&*c, &major, &grade, section, jalali_year, jalali_month)?;
        let all = db::get_classes(&*c)?;
        let show_sec = all.iter().filter(|x| x.major == major && x.grade == grade).count() > 1;
        reports::export_monthly_xlsx(&r, &major, &grade, section, show_sec)
    }

    pub fn export_monthly_csv(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<String, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let r = db::get_monthly_report(&*c, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&r, &major, &grade, section))
    }

    pub fn export_template_xlsx(&self) -> Result<Vec<u8>, CoreError> { reports::export_template_xlsx() }

    pub fn export_backup_json(&self) -> Result<String, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::export_backup_json(&*c)
    }

    pub fn restore_backup_json(&self, json_text: String) -> Result<ImportReport, CoreError> {
        let mut c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::restore_backup_json(&mut *c, &json_text)
    }

    pub fn format_jalali_date(&self, date_iso: String) -> String { persian::format_iso_to_jalali(&date_iso) }

    pub fn get_jalali_year_month(&self, date_iso: String) -> JalaliYearMonth {
        let (y, m) = persian::iso_to_jalali_year_month(&date_iso);
        JalaliYearMonth { year: y, month: m as i32, label: persian::format_jalali_month_label(y, m) }
    }

    pub fn get_jalali_month_grid(&self, jalali_year: i32, jalali_month: i32) -> JalaliMonthGrid {
        persian::build_jalali_month_grid(jalali_year, jalali_month)
    }

    pub fn set_setting(&self, key: String, value: String) -> Result<(), CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_setting(&*c, &key, &value)
    }

    pub fn get_setting(&self, key: String) -> Result<String, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_setting(&*c, &key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const SAMPLE: &str = "ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل\n\
1,نمونه,الکتروتکنیک,دهم,1,علی,رضایی,حسن,4700153423,9170327544\n\
2,نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153424,9170327545\n\
3,نمونه,صنایع شیمیایی,یازدهم,2,ابراهیم,احمدی,راشد,4700153425,9170327546\n";

    #[test]
    fn test_v51_late_minutes_single_branch_and_borrows() {
        let e = AttendanceEngine::new(":memory:".into()).unwrap();
        e.import_file_bytes("s.csv".into(), SAMPLE.as_bytes().to_vec(), true).unwrap();
        let elec = e.get_class_attendance("الکتروتکنیک".into(), "دهم".into(), 1, "2025-11-26".into(), Period::First, "".into()).unwrap();
        let sid = elec.students[0].student_id;

        e.set_attendance(sid, "2025-11-26".into(), Period::First, AttendanceStatus::Late, "10".into(), "ترافیک".into(), "دبیر".into(), "برق".into(), "08:00".into()).unwrap();
        e.set_attendance(sid, "2025-11-26".into(), Period::Second, AttendanceStatus::Excused, "".into(), "".into(), "دبیر".into(), "برق".into(), "09:00".into()).unwrap();

        let rep = e.generate_principal_report("الکتروتکنیک".into(), "دهم".into(), 1, "2025-11-26".into(), false, "دبیر".into()).unwrap();
        assert!(!rep.full_text.contains("شعبه"));
        assert!(rep.sms_text.contains("تأخیر ۱۰ دقیقه"));
        assert!(rep.sms_text.contains("غیبت موجه"));

        let details = e.get_student_monthly_details(sid, 1404, 9).unwrap();
        assert_eq!(details.len(), 2);
        assert_eq!(details[0].event_time, "10");
    }
}
''',
}


def main():
    for rel, content in FILES.items():
        p = Path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
        print(f"Created: {rel}")
    print(f"\nPart 1 (Rust Core v5.1) done: {len(FILES)} files.")


if __name__ == "__main__":
    main()
