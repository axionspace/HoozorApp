from pathlib import Path

FILES = {
    "rust-core/Cargo.toml": r'''[package]
name = "hozoor_core"
version = "3.0.0"
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

    "rust-core/uniffi-bindgen.rs": r'''fn main() {
    uniffi::uniffi_bindgen_main()
}
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
pub enum Period {
    First,
    Second,
    Third,
    Fourth,
}

impl Period {
    pub fn to_i32(self) -> i32 {
        match self {
            Period::First => 1,
            Period::Second => 2,
            Period::Third => 3,
            Period::Fourth => 4,
        }
    }

    pub fn previous(self) -> Option<Period> {
        match self {
            Period::First => None,
            Period::Second => Some(Period::First),
            Period::Third => Some(Period::Second),
            Period::Fourth => Some(Period::Third),
        }
    }

    pub fn label_fa(self) -> &'static str {
        match self {
            Period::First => "زنگ اول",
            Period::Second => "زنگ دوم",
            Period::Third => "زنگ سوم",
            Period::Fourth => "زنگ چهارم",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, uniffi::Enum)]
pub enum AttendanceStatus {
    Unmarked,
    Present,
    Absent,
    Late,
    Excused,
}

impl AttendanceStatus {
    pub fn to_i32(self) -> i32 {
        match self {
            AttendanceStatus::Unmarked => 0,
            AttendanceStatus::Present => 1,
            AttendanceStatus::Absent => 2,
            AttendanceStatus::Late => 3,
            AttendanceStatus::Excused => 4,
        }
    }

    pub fn from_i32(v: i32) -> Self {
        match v {
            1 => AttendanceStatus::Present,
            2 => AttendanceStatus::Absent,
            3 => AttendanceStatus::Late,
            4 => AttendanceStatus::Excused,
            _ => AttendanceStatus::Unmarked,
        }
    }

    pub fn label_fa(self) -> &'static str {
        match self {
            AttendanceStatus::Unmarked => "حاضر",
            AttendanceStatus::Present => "حاضر",
            AttendanceStatus::Absent => "غایب",
            AttendanceStatus::Late => "تأخیر",
            AttendanceStatus::Excused => "غیبت موجه",
        }
    }
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct ClassGroup {
    pub school_name: String,
    pub major: String,
    pub grade: String,
    pub section: i32,
    pub student_count: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct StudentAttendanceRow {
    pub student_id: i64,
    pub row_num: i32,
    pub first_name: String,
    pub last_name: String,
    pub father_name: String,
    pub national_id: String,
    pub mobile: String,
    pub current_status: AttendanceStatus,
    pub period_statuses: Vec<AttendanceStatus>,
    pub class_score: String,
    pub session_score: String,
    pub note: String,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct PeriodSummary {
    pub total: i32,
    pub present: i32,
    pub absent: i32,
    pub late: i32,
    pub excused: i32,
    pub unmarked: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct ClassAttendanceSnapshot {
    pub jalali_date: String,
    pub is_period_saved: bool,
    pub summary: PeriodSummary,
    pub students: Vec<StudentAttendanceRow>,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct ImportReport {
    pub imported_count: i32,
    pub skipped_count: i32,
    pub classes_count: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct PrincipalReportBundle {
    pub full_text: String,
    pub sms_text: String,
    pub full_day_absent_count: i32,
    pub partial_absent_count: i32,
    pub late_count: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct BackupStats {
    pub students_count: i32,
    pub classes_count: i32,
    pub attendance_count: i32,
    pub scores_count: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct TopStudentCount {
    pub full_name: String,
    pub count: i32,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct ClassAnalytics {
    pub student_count: i32,
    pub recorded_sessions: i32,
    pub total_absent: i32,
    pub total_late: i32,
    pub total_excused: i32,
    pub top_absent: Vec<TopStudentCount>,
    pub top_late: Vec<TopStudentCount>,
    pub top_excused: Vec<TopStudentCount>,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct MonthlyStudentStat {
    pub student_id: i64,
    pub first_name: String,
    pub last_name: String,
    pub father_name: String,
    pub national_id: String,
    pub mobile: String,
    pub class_score: String,
    pub present_periods: i32,
    pub absent_periods: i32,
    pub full_absent_days: i32,
    pub late_periods: i32,
    pub excused_periods: i32,
    pub attendance_percent: f64,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct MonthlyClassReport {
    pub jalali_year: i32,
    pub jalali_month: i32,
    pub month_label: String,
    pub recorded_days: i32,
    pub average_attendance_percent: f64,
    pub total_absent_periods: i32,
    pub total_full_absent_days: i32,
    pub students: Vec<MonthlyStudentStat>,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct JalaliYearMonth {
    pub year: i32,
    pub month: i32,
    pub label: String,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct JalaliDayCell {
    pub day: i32,
    pub date_iso: String,
    pub is_friday: bool,
}

#[derive(Debug, Clone, uniffi::Record)]
pub struct JalaliMonthGrid {
    pub year: i32,
    pub month: i32,
    pub month_label: String,
    pub leading_blanks: i32,
    pub days: Vec<JalaliDayCell>,
}
''',

    "rust-core/src/persian.rs": r'''use crate::models::{JalaliDayCell, JalaliMonthGrid};

pub fn normalize_persian(input: &str) -> String {
    let mut out = String::with_capacity(input.len());
    for ch in input.trim().chars() {
        let mapped = match ch {
            'ي' | 'ى' => 'ی',
            'ك' => 'ک',
            'ة' | 'ۀ' => 'ه',
            'ؤ' => 'و',
            'إ' | 'أ' => 'ا',
            '۰' | '٠' => '0',
            '۱' | '١' => '1',
            '۲' | '٢' => '2',
            '۳' | '٣' => '3',
            '۴' | '٤' => '4',
            '۵' | '٥' => '5',
            '۶' | '٦' => '6',
            '۷' | '٧' => '7',
            '۸' | '٨' => '8',
            '۹' | '٩' => '9',
            '\u{0640}' | '\u{064B}'..='\u{065F}' => continue,
            _ => ch,
        };
        out.push(mapped);
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
    let digits: String = normalize_persian(raw).chars().filter(|c| c.is_ascii_digit()).collect();
    if digits.is_empty() { return String::new(); }
    if digits.len() < 10 { format!("{:0>10}", digits) } else { digits.chars().take(10).collect() }
}

pub fn normalize_mobile(raw: &str) -> String {
    let digits: String = normalize_persian(raw).chars().filter(|c| c.is_ascii_digit()).collect();
    if digits.len() == 10 && digits.starts_with('9') { format!("0{digits}") }
    else if digits.len() == 12 && digits.starts_with("98") { format!("0{}", &digits[2..]) }
    else { digits }
}

pub fn grade_rank(grade: &str) -> i32 {
    match normalize_persian(grade).as_str() {
        "اول" => 1, "دوم" => 2, "سوم" => 3, "چهارم" => 4, "پنجم" => 5, "ششم" => 6,
        "هفتم" => 7, "هشتم" => 8, "نهم" => 9, "دهم" => 10, "یازدهم" => 11, "دوازدهم" => 12, _ => 99,
    }
}

pub fn is_middle_grade(grade: &str) -> bool {
    matches!(normalize_persian(grade).as_str(), "هفتم" | "هشتم" | "نهم")
}

pub fn format_iso_to_jalali(date_iso: &str) -> String {
    let p: Vec<&str> = date_iso.split('-').collect();
    if p.len() != 3 { return to_persian_digits(date_iso); }
    let (Ok(gy), Ok(gm), Ok(gd)) = (p[0].parse::<i32>(), p[1].parse::<u32>(), p[2].parse::<u32>()) else { return to_persian_digits(date_iso); };
    if !(1..=12).contains(&gm) || !(1..=31).contains(&gd) { return to_persian_digits(date_iso); }
    let (jy, jm, jd) = gregorian_to_jalali(gy, gm, gd);
    to_persian_digits(&format!("{} {jd} {} {jy}", weekday_fa(gy, gm, gd), month_name_fa(jm)))
}

pub fn format_iso_to_jalali_short(date_iso: &str) -> String {
    let p: Vec<&str> = date_iso.split('-').collect();
    if p.len() == 3 {
        if let (Ok(gy), Ok(gm), Ok(gd)) = (p[0].parse::<i32>(), p[1].parse::<u32>(), p[2].parse::<u32>()) {
            let (jy, jm, jd) = gregorian_to_jalali(gy, gm, gd);
            return to_persian_digits(&format!("{jd} {} {jy}", month_name_fa(jm)));
        }
    }
    to_persian_digits(date_iso)
}

pub fn iso_to_jalali_year_month(date_iso: &str) -> (i32, u32) {
    let p: Vec<&str> = date_iso.split('-').collect();
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
    let is_leap = (gy % 4 == 0 && gy % 100 != 0) || (gy % 400 == 0);
    let sal_a = [0, 31, if is_leap { 29 } else { 28 }, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let mut gm = 1u32;
    while gm <= 12 && gd > sal_a[gm as usize] { gd -= sal_a[gm as usize]; gm += 1; }
    (gy, gm, gd as u32)
}

pub fn jalali_month_days(jy: i32, jm: u32) -> u32 {
    match jm {
        1..=6 => 31, 7..=11 => 30,
        12 => {
            let (gy, gm, gd) = jalali_to_gregorian(jy, 12, 30);
            if gregorian_to_jalali(gy, gm, gd) == (jy, 12, 30) { 30 } else { 29 }
        }
        _ => 30,
    }
}

pub fn jalali_month_range_iso(jy: i32, jm: u32) -> (String, String) {
    let last_day = jalali_month_days(jy, jm);
    let (sy, sm, sd) = jalali_to_gregorian(jy, jm, 1);
    let (ey, em, ed) = jalali_to_gregorian(jy, jm, last_day);
    (format!("{sy:04}-{sm:02}-{sd:02}"), format!("{ey:04}-{em:02}-{ed:02}"))
}

pub fn format_jalali_month_label(jy: i32, jm: u32) -> String {
    to_persian_digits(&format!("{} {}", month_name_fa(jm), jy))
}

pub fn build_jalali_month_grid(jy: i32, jm_i32: i32) -> JalaliMonthGrid {
    let jm = jm_i32.clamp(1, 12) as u32;
    let total_days = jalali_month_days(jy, jm);
    let (fy, fm, fd) = jalali_to_gregorian(jy, jm, 1);
    let first_fa_wd = (sunday_based_weekday(fy, fm, fd) + 1) % 7;
    let mut days = Vec::with_capacity(total_days as usize);
    for d in 1..=total_days {
        let (gy, gm, gd) = jalali_to_gregorian(jy, jm, d);
        days.push(JalaliDayCell { day: d as i32, date_iso: format!("{gy:04}-{gm:02}-{gd:02}"), is_friday: (sunday_based_weekday(gy, gm, gd) + 1) % 7 == 6 });
    }
    JalaliMonthGrid { year: jy, month: jm as i32, month_label: format_jalali_month_label(jy, jm), leading_blanks: first_fa_wd as i32, days }
}

fn sunday_based_weekday(y: i32, m: u32, d: u32) -> usize {
    let t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4];
    let y = if m < 3 { y - 1 } else { y };
    (y + y / 4 - y / 100 + y / 400 + t[(m - 1) as usize] + d as i32).rem_euclid(7) as usize
}

fn weekday_fa(y: i32, m: u32, d: u32) -> &'static str {
    const W: [&str; 7] = ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"];
    W[sunday_based_weekday(y, m, d)]
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

struct ParsedStudent {
    row_num: i32, school_name: String, major: String, grade: String, section: i32,
    first_name: String, last_name: String, father_name: String, national_id: String, mobile: String, search_key: String,
}

pub fn import_file_bytes(conn: &mut Connection, file_name: &str, bytes: &[u8], replace_existing: bool) -> Result<ImportReport, CoreError> {
    if bytes.is_empty() { return Err(CoreError::Import("فایل انتخاب‌شده خالی است".into())); }
    let lower = file_name.to_lowercase();
    let is_xlsx = bytes.len() >= 4 && &bytes[0..4] == b"PK\x03\x04";
    let is_xls = bytes.len() >= 4 && &bytes[0..4] == b"\xD0\xCF\x11\xE0";
    if is_xlsx || is_xls || lower.ends_with(".xlsx") || lower.ends_with(".xls") {
        let mut wb = open_workbook_auto_from_rs(Cursor::new(bytes)).map_err(|e| CoreError::Import(format!("فایل اکسل قابل خواندن نیست: {e}")))?;
        let names = wb.sheet_names().to_vec();
        let sheet = names.iter().find(|n| n.contains("دانش") || n.contains("آموز")).cloned().or_else(|| names.into_iter().next()).ok_or_else(|| CoreError::Import("فایل اکسل شیت ندارد".into()))?;
        let range = wb.worksheet_range(&sheet).map_err(|e| CoreError::Import(format!("خطا در خواندن شیت: {e}")))?;
        let rows: Vec<Vec<String>> = range.rows().map(|r| r.iter().map(cell_to_string).collect()).collect();
        persist_rows(conn, &rows, replace_existing)
    } else {
        let text = String::from_utf8(bytes.to_vec()).map_err(|_| CoreError::Import("فایل CSV باید UTF-8 باشد یا از فایل اکسل (.xlsx) استفاده کنید".into()))?;
        let cleaned = text.trim_start_matches('\u{FEFF}');
        let first = cleaned.lines().find(|l| !l.trim().is_empty()).ok_or_else(|| CoreError::Import("فایل CSV خالی است".into()))?;
        let delim = detect_delim(first);
        let rows: Vec<Vec<String>> = cleaned.lines().filter(|l| !l.trim().is_empty()).map(|l| parse_csv_line(l, delim)).collect();
        persist_rows(conn, &rows, replace_existing)
    }
}

fn detect_delim(s: &str) -> char {
    let (c, sc, t) = (s.matches(',').count(), s.matches(';').count(), s.matches('\t').count());
    if sc > c && sc >= t { ';' } else if t > c && t > sc { '\t' } else { ',' }
}

fn parse_csv_line(line: &str, delim: char) -> Vec<String> {
    let mut fields = Vec::with_capacity(10);
    let mut cur = String::new();
    let mut quoted = false;
    let mut it = line.chars().peekable();
    while let Some(c) = it.next() {
        if quoted {
            if c == '"' { if it.peek() == Some(&'"') { it.next(); cur.push('"'); } else { quoted = false; } }
            else { cur.push(c); }
        } else if c == '"' { quoted = true; }
        else if c == delim { fields.push(cur.trim().to_string()); cur.clear(); }
        else { cur.push(c); }
    }
    fields.push(cur.trim().to_string());
    fields
}

fn cell_to_string(cell: &Data) -> String {
    match cell {
        Data::String(s) => s.trim().to_string(),
        Data::Int(i) => i.to_string(),
        Data::Float(f) => if f.fract() == 0.0 { format!("{}", *f as i64) } else { f.to_string() },
        Data::Bool(b) => b.to_string(),
        Data::DateTime(dt) => dt.as_f64().to_string(),
        _ => String::new(),
    }
}

fn persist_rows(conn: &mut Connection, raw_rows: &[Vec<String>], replace_existing: bool) -> Result<ImportReport, CoreError> {
    if raw_rows.is_empty() { return Err(CoreError::Import("فایل خالی است".into())); }
    let has_header = raw_rows[0].iter().map(|c| normalize_persian(c)).any(|c| c.contains("ردیف") || c.contains("نام خانوادگی") || c.contains("کد ملی"));
    let start = if has_header { 1 } else { 0 };

    let mut students = Vec::with_capacity(raw_rows.len());
    let mut skipped = 0i32;
    for (idx, cols) in raw_rows[start..].iter().enumerate() {
        if cols.len() < 9 { skipped += 1; continue; }
        let row_num = normalize_persian(&cols[0]).parse::<i32>().unwrap_or((idx + 1) as i32);
        let school_name = { let s = cols[1].trim(); if s.is_empty() { "آموزشگاه".to_string() } else { s.to_string() } };
        let grade = cols[3].trim().to_string();
        let major = if is_middle_grade(&grade) { String::new() } else { cols[2].trim().to_string() };
        let section = normalize_persian(&cols[4]).parse::<i32>().unwrap_or(1).max(1);
        let first_name = cols[5].trim().to_string();
        let last_name = cols[6].trim().to_string();
        let father_name = cols[7].trim().to_string();
        let national_id = normalize_national_id(&cols[8]);
        let mobile = cols.get(9).map(|m| normalize_mobile(m)).unwrap_or_default();
        if first_name.is_empty() || last_name.is_empty() || grade.is_empty() || national_id.is_empty() { skipped += 1; continue; }
        let search_key = normalize_persian(&format!("{first_name} {last_name} {father_name} {national_id} {mobile}"));
        students.push(ParsedStudent { row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, search_key });
    }
    if students.is_empty() { return Err(CoreError::Import("هیچ دانش‌آموز معتبری یافت نشد".into())); }

    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    if replace_existing { tx.execute("DELETE FROM students", []).map_err(|e| CoreError::Database(e.to_string()))?; }
    {
        let mut stmt = tx.prepare_cached(
            "INSERT INTO students (row_num, school_name, major, grade, section, first_name, last_name, father_name, national_id, mobile, search_key)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)
             ON CONFLICT(national_id) DO UPDATE SET
                 row_num = excluded.row_num, school_name = excluded.school_name, major = excluded.major,
                 grade = excluded.grade, section = excluded.section, first_name = excluded.first_name,
                 last_name = excluded.last_name, father_name = excluded.father_name, mobile = excluded.mobile, search_key = excluded.search_key",
        ).map_err(|e| CoreError::Database(e.to_string()))?;
        for s in &students {
            stmt.execute(params![s.row_num, s.school_name, s.major, s.grade, s.section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, s.search_key])
                .map_err(|e| CoreError::Database(e.to_string()))?;
        }
    }
    let classes_count: i32 = tx.query_row("SELECT COUNT(*) FROM (SELECT DISTINCT major, grade, section FROM students)", [], |r| r.get(0)).map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;
    Ok(ImportReport { imported_count: students.len() as i32, skipped_count: skipped, classes_count })
}
''',

    "rust-core/src/db.rs": r'''use crate::models::{
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
''',

    "rust-core/src/reports.rs": r'''use crate::db;
use crate::models::{AttendanceStatus, ClassGroup, CoreError, MonthlyClassReport, Period, PrincipalReportBundle};
use crate::persian::{format_iso_to_jalali, format_iso_to_jalali_short, to_persian_digits};
use rusqlite::Connection;
use rust_xlsxwriter::{Color, Format, FormatAlign, Workbook};
use std::collections::HashSet;

const PERIOD_NAMES_FULL: [&str; 4] = ["زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
const PERIOD_NAMES_SMS: [&str; 4] = ["زنگ ۱", "زنگ ۲", "زنگ ۳", "زنگ ۴"];

fn format_class_title(major: &str, grade: &str, section: i32) -> String {
    let sec = to_persian_digits(&section.to_string());
    if major.trim().is_empty() { format!("پایه {grade} شعبه {sec}") } else { format!("{major} - {grade} شعبه {sec}") }
}

pub fn generate_period_group_message(
    conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, period: Period,
    target_status: AttendanceStatus, teacher_name: &str, lesson_name: &str, whole_school: bool,
) -> Result<String, CoreError> {
    let classes: Vec<ClassGroup> = if whole_school {
        db::get_classes(conn)?
    } else {
        db::get_classes(conn)?.into_iter().filter(|c| c.major == major && c.grade == grade && c.section == section).collect()
    };
    if classes.is_empty() { return Err(CoreError::InvalidInput("هیچ کلاسی یافت نشد".into())); }

    let action = if target_status == AttendanceStatus::Late { "با تأخیر حاضر شده‌اند" } else { "غایب بوده‌اند" };
    let jalali = format_iso_to_jalali_short(date_iso);
    let lesson_part = if lesson_name.trim().is_empty() { String::new() } else { format!("در درس {} ", lesson_name.trim()) };
    let school = &classes[0].school_name;

    let mut body = String::new();
    let mut total_matched = 0usize;

    for cls in &classes {
        let snap = db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, period, "")?;
        let matched: Vec<_> = snap.students.into_iter().filter(|s| s.current_status == target_status).collect();
        if matched.is_empty() { continue; }
        if whole_school {
            body.push_str(&format!("\n[{}]\n", format_class_title(&cls.major, &cls.grade, cls.section)));
        }
        for (i, s) in matched.iter().enumerate() {
            total_matched += 1;
            let num = to_persian_digits(&(i + 1).to_string());
            let fa = if s.father_name.is_empty() { "ثبت نشده" } else { &s.father_name };
            let tag = if target_status == AttendanceStatus::Late { "تأخیر" } else { "غایب" };
            body.push_str(&format!("{num}. {} {}، فرزند {fa} ({tag})\n", s.first_name, s.last_name));
        }
    }

    if total_matched == 0 {
        let word = if target_status == AttendanceStatus::Late { "تأخیری" } else { "غایبی" };
        return Err(CoreError::InvalidInput(format!("در {} هیچ دانش‌آموز {word} ثبت نشده است", period.label_fa())));
    }

    let scope = if whole_school { format!("کل {school}") } else { format_class_title(major, grade, section) };
    let mut msg = format!("سلام علیکم\nمدیریت محترم {school}،\nدانش‌آموزان زیر {lesson_part}{scope}، {} مورخه {jalali} {action}:\n\n{}", period.label_fa(), body.trim());
    if !teacher_name.trim().is_empty() {
        msg.push_str(&format!("\n\nبا تشکر\n{}", teacher_name.trim()));
    }
    Ok(msg)
}

/// گزارش هوشمند مدیر + متن فشرده پیامک با ذکر دقیق (غایب / تأخیر / موجه / حاضر) و عدم تکرار غایب کل روز
pub fn generate_principal_report(
    conn: &Connection, major: Option<&str>, grade: Option<&str>, section: Option<i32>, date_iso: &str, teacher_name: &str,
) -> Result<PrincipalReportBundle, CoreError> {
    let all = db::get_classes(conn)?;
    let classes: Vec<ClassGroup> = match (major, grade, section) {
        (Some(m), Some(g), Some(sec)) => all.into_iter().filter(|c| c.major == m && c.grade == g && c.section == sec).collect(),
        _ => all,
    };
    if classes.is_empty() { return Err(CoreError::InvalidInput("هیچ کلاسی یافت نشد".into())); }

    let jalali_full = format_iso_to_jalali(date_iso);
    let jalali_short = format_iso_to_jalali_short(date_iso);
    let school = &classes[0].school_name;
    let is_whole = classes.len() > 1;

    let mut full = format!("📋 گزارش حضور و غیاب {school}\n📅 تاریخ: {jalali_full}\n");
    if !teacher_name.trim().is_empty() { full.push_str(&format!("👤 دبیر: {}\n", teacher_name.trim())); }
    let mut sms = if is_whole {
        format!("گزارش حضور و غیاب {school} ({jalali_short})\n")
    } else {
        let c = &classes[0];
        let t = format_class_title(&c.major, &c.grade, c.section);
        full.push_str(&format!("🏫 کلاس: {t}\n"));
        format!("گزارش {t} ({jalali_short})\n")
    };

    let (mut total_full_day, mut total_partial, mut total_late) = (0, 0, 0);
    let mut any_data = false;

    for cls in &classes {
        let snap = db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?;
        let active_periods: Vec<usize> = (0..4).filter(|&p| snap.students.iter().any(|s| s.period_statuses[p] != AttendanceStatus::Unmarked)).collect();
        if active_periods.is_empty() { continue; }
        any_data = true;

        let mut full_day_ids = HashSet::new();
        let mut full_day_full = Vec::new();
        let mut full_day_sms = Vec::new();
        if active_periods.len() >= 2 {
            for s in &snap.students {
                if active_periods.iter().all(|&p| matches!(s.period_statuses[p], AttendanceStatus::Absent | AttendanceStatus::Excused)) {
                    full_day_ids.insert(s.student_id);
                    let all_exc = active_periods.iter().all(|&p| s.period_statuses[p] == AttendanceStatus::Excused);
                    let tag = if all_exc { "موجه" } else { "غایب" };
                    full_day_full.push(format!("{} {} ({tag})", s.first_name, s.last_name));
                    full_day_sms.push(format!("{} {}({tag})", s.first_name, s.last_name));
                }
            }
        }

        let mut per_period = Vec::new();
        let mut has_issue = !full_day_full.is_empty();
        for &p in &active_periods {
            let (mut f_items, mut s_items) = (Vec::new(), Vec::new());
            let mut present_cnt = 0i32;
            for s in &snap.students {
                let st = s.period_statuses[p];
                if matches!(st, AttendanceStatus::Present | AttendanceStatus::Unmarked) { present_cnt += 1; }
                if full_day_ids.contains(&s.student_id) { continue; }
                match st {
                    AttendanceStatus::Absent => { total_partial += 1; has_issue = true; f_items.push(format!("{} {} (غایب)", s.first_name, s.last_name)); s_items.push(format!("{} {}(غایب)", s.first_name, s.last_name)); }
                    AttendanceStatus::Excused => { total_partial += 1; has_issue = true; f_items.push(format!("{} {} (موجه)", s.first_name, s.last_name)); s_items.push(format!("{} {}(موجه)", s.first_name, s.last_name)); }
                    AttendanceStatus::Late => { total_late += 1; has_issue = true; f_items.push(format!("{} {} (تأخیر)", s.first_name, s.last_name)); s_items.push(format!("{} {}(تأخیر)", s.first_name, s.last_name)); }
                    _ => {}
                }
            }
            per_period.push((p, present_cnt, f_items, s_items));
        }

        total_full_day += full_day_full.len() as i32;
        if is_whole {
            if !has_issue { continue; }
            let hdr = format_class_title(&cls.major, &cls.grade, cls.section);
            full.push_str(&format!("\n────────────\n🏫 {hdr}\n"));
            sms.push_str(&format!("\n[{hdr}]\n"));
        } else {
            full.push_str("────────────────────\n");
        }

        if !has_issue {
            let total_fa = to_persian_digits(&snap.students.len().to_string());
            full.push_str(&format!("✅ همه {total_fa} دانش‌آموز در زنگ‌های ثبت‌شده حاضر بودند.\n"));
            sms.push_str(&format!("وضعیت: همه {total_fa} نفر حاضر\n"));
            continue;
        }
        if !full_day_full.is_empty() {
            let cnt = to_persian_digits(&full_day_full.len().to_string());
            full.push_str(&format!("🔴 غایبین کل روز ({cnt} نفر):\n"));
            for name in &full_day_full { full.push_str(&format!("• {name}\n")); }
            sms.push_str(&format!("غایب کل روز: {}\n", full_day_sms.join("، ")));
        }
        for (p, present_cnt, f_items, s_items) in per_period {
            let p_fa = to_persian_digits(&present_cnt.to_string());
            if f_items.is_empty() {
                if !is_whole {
                    full.push_str(&format!("\n🔔 {} ({p_fa} حاضر):\n• بقیه همه حاضر بودند\n", PERIOD_NAMES_FULL[p]));
                    sms.push_str(&format!("{}: بقیه حاضر ({p_fa} نفر)\n", PERIOD_NAMES_SMS[p]));
                }
            } else {
                full.push_str(&format!("\n🔔 {} ({p_fa} حاضر):\n", PERIOD_NAMES_FULL[p]));
                for item in &f_items { full.push_str(&format!("• {item}\n")); }
                sms.push_str(&format!("{}: {} | {p_fa} حاضر\n", PERIOD_NAMES_SMS[p], s_items.join("، ")));
            }
        }
    }

    if !any_data {
        full.push_str("\nهنوز هیچ حضور و غیابی برای این تاریخ ثبت نشده است (پیش‌فرض همه حاضر).");
        sms.push_str("وضعیت: همه حاضر (تغییری ثبت نشده)");
    } else if is_whole && total_full_day == 0 && total_partial == 0 && total_late == 0 {
        full.push_str("\n✅ امروز در تمام کلاس‌های ثبت‌شده، همه دانش‌آموزان حاضر بودند.");
        sms.push_str("وضعیت کل مدرسه: همه حاضر");
    }

    Ok(PrincipalReportBundle { full_text: full.trim().to_string(), sms_text: sms.trim().to_string(), full_day_absent_count: total_full_day, partial_absent_count: total_partial, late_count: total_late })
}

pub fn export_daily_csv(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str) -> Result<String, CoreError> {
    let snap = db::get_class_attendance(conn, major, grade, section, date_iso, Period::First, "")?;
    let mut csv = String::with_capacity(snap.students.len() * 140 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل,نمره,تاریخ,زنگ اول,زنگ دوم,زنگ سوم,زنگ چهارم\n");
    for (idx, s) in snap.students.iter().enumerate() {
        csv.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
            idx + 1, major, grade, section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, s.class_score, snap.jalali_date,
            s.period_statuses[0].label_fa(), s.period_statuses[1].label_fa(), s.period_statuses[2].label_fa(), s.period_statuses[3].label_fa(),
        ));
    }
    Ok(csv)
}

pub fn export_daily_xlsx(conn: &Connection, major: &str, grade: &str, section: i32, date_iso: &str, all_classes: bool) -> Result<Vec<u8>, CoreError> {
    let all = db::get_classes(conn)?;
    let classes: Vec<ClassGroup> = if all_classes { all } else { all.into_iter().filter(|c| c.major == major && c.grade == grade && c.section == section).collect() };
    if classes.is_empty() { return Err(CoreError::InvalidInput("هیچ کلاسی برای خروجی وجود ندارد".into())); }

    let mut wb = Workbook::new();
    let header_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x1B5E20)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cell_fmt = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    let present_fmt = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xD7F5E6)).set_font_color(Color::RGB(0x1B5E20)).set_align(FormatAlign::Center);
    let absent_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFDADF)).set_font_color(Color::RGB(0xB71C1C)).set_align(FormatAlign::Center);
    let late_fmt = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFECC7)).set_font_color(Color::RGB(0x9A5B00)).set_align(FormatAlign::Center);
    let excused_fmt = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xDCE7FF)).set_font_color(Color::RGB(0x1A47A6)).set_align(FormatAlign::Center);

    let headers = ["ردیف", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل", "نمره", "تاریخ", "زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
    let mut used = HashSet::new();
    for cls in classes {
        let snap = db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?;
        let sheet = wb.add_worksheet();
        let raw = if cls.major.is_empty() { format!("{} {}", cls.grade, cls.section) } else { format!("{} {} {}", cls.major, cls.grade, cls.section) };
        sheet.set_name(&unique_sheet_name(&raw, &mut used)).map_err(|e| CoreError::Import(e.to_string()))?;
        sheet.set_right_to_left(true);
        for (c, h) in headers.iter().enumerate() { let _ = sheet.write_string_with_format(0, c as u16, *h, &header_fmt); }
        for (idx, s) in snap.students.iter().enumerate() {
            let r = (idx + 1) as u32;
            let _ = sheet.write_number_with_format(r, 0, (idx + 1) as f64, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 1, &s.first_name, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 2, &s.last_name, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 3, &s.father_name, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 4, &s.national_id, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 5, &s.mobile, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 6, &s.class_score, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 7, &snap.jalali_date, &cell_fmt);
            for p in 0..4 {
                let st = s.period_statuses[p];
                let fmt = match st {
                    AttendanceStatus::Absent => &absent_fmt,
                    AttendanceStatus::Late => &late_fmt,
                    AttendanceStatus::Excused => &excused_fmt,
                    _ => &present_fmt,
                };
                let _ = sheet.write_string_with_format(r, (8 + p) as u16, st.label_fa(), fmt);
            }
        }
        sheet.autofit();
    }
    wb.save_to_buffer().map_err(|e| CoreError::Import(format!("خطا در ساخت اکسل: {e}")))
}

pub fn export_monthly_xlsx(report: &MonthlyClassReport, major: &str, grade: &str, section: i32) -> Result<Vec<u8>, CoreError> {
    let mut wb = Workbook::new();
    let sheet = wb.add_worksheet();
    let mut used = HashSet::new();
    sheet.set_name(&unique_sheet_name(&format!("ماهانه {}", report.month_label), &mut used)).map_err(|e| CoreError::Import(e.to_string()))?;
    sheet.set_right_to_left(true);
    let header_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x0D47A1)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cell_fmt = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    let warn_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFDADF)).set_font_color(Color::RGB(0xB71C1C)).set_align(FormatAlign::Center);

    let headers = ["ردیف", "کلاس", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "موبایل", "نمره", "زنگ حاضر", "زنگ غایب", "غیبت کل روز", "تأخیر", "موجه", "درصد حضور"];
    for (c, h) in headers.iter().enumerate() { let _ = sheet.write_string_with_format(0, c as u16, *h, &header_fmt); }
    let cls_label = format_class_title(major, grade, section);
    for (idx, s) in report.students.iter().enumerate() {
        let r = (idx + 1) as u32;
        let _ = sheet.write_number_with_format(r, 0, (idx + 1) as f64, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 1, &cls_label, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 2, &s.first_name, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 3, &s.last_name, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 4, &s.father_name, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 5, &s.national_id, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 6, &s.mobile, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 7, &s.class_score, &cell_fmt);
        let _ = sheet.write_number_with_format(r, 8, s.present_periods as f64, &cell_fmt);
        let af = if s.absent_periods > 0 { &warn_fmt } else { &cell_fmt };
        let _ = sheet.write_number_with_format(r, 9, s.absent_periods as f64, af);
        let _ = sheet.write_number_with_format(r, 10, s.full_absent_days as f64, af);
        let _ = sheet.write_number_with_format(r, 11, s.late_periods as f64, &cell_fmt);
        let _ = sheet.write_number_with_format(r, 12, s.excused_periods as f64, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 13, &format!("{}٪", to_persian_digits(&format!("{:.1}", s.attendance_percent))), &cell_fmt);
    }
    sheet.autofit();
    wb.save_to_buffer().map_err(|e| CoreError::Import(format!("خطا در اکسل ماهانه: {e}")))
}

pub fn export_monthly_csv(report: &MonthlyClassReport, major: &str, grade: &str, section: i32) -> String {
    let mut csv = String::with_capacity(report.students.len() * 120 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,ماه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,موبایل,نمره,زنگ حاضر,زنگ غایب,غیبت کل روز,تأخیر,موجه,درصد حضور\n");
    for (idx, s) in report.students.iter().enumerate() {
        csv.push_str(&format!("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.1}%\n",
            idx + 1, report.month_label, major, grade, section, s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, s.class_score,
            s.present_periods, s.absent_periods, s.full_absent_days, s.late_periods, s.excused_periods, s.attendance_percent));
    }
    csv
}

pub fn export_template_xlsx() -> Result<Vec<u8>, CoreError> {
    let mut wb = Workbook::new();
    let sheet = wb.add_worksheet();
    sheet.set_name("دانش‌آموزان").map_err(|e| CoreError::Import(e.to_string()))?;
    sheet.set_right_to_left(true);
    let hf = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x145548)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cf = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    for (c, h) in ["ردیف", "نام مدرسه", "رشته", "پایه", "شعبه", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل"].iter().enumerate() {
        let _ = sheet.write_string_with_format(0, c as u16, *h, &hf);
    }
    let sample = [
        ["1", "آموزشگاه نمونه", "صنایع شیمیایی", "دهم", "1", "علی", "احمدی", "حسن", "1000000001", "09121234561"],
        ["2", "آموزشگاه نمونه", "الکتروتکنیک", "یازدهم", "1", "رضا", "محمدی", "مهدی", "1000000002", "09121234562"],
        ["3", "آموزشگاه نمونه", "ساختمان", "دوازدهم", "2", "امیر", "کریمی", "سعید", "1000000003", "09121234563"],
    ];
    for (ri, row) in sample.iter().enumerate() {
        for (ci, val) in row.iter().enumerate() { let _ = sheet.write_string_with_format((ri + 1) as u32, ci as u16, *val, &cf); }
    }
    sheet.autofit();
    wb.save_to_buffer().map_err(|e| CoreError::Import(format!("خطا در ساخت نمونه: {e}")))
}

fn unique_sheet_name(raw: &str, used: &mut HashSet<String>) -> String {
    let clean: String = raw.chars().filter(|c| !matches!(c, ':' | '\\' | '/' | '?' | '*' | '[' | ']')).collect();
    let mut base: String = clean.chars().take(28).collect();
    if base.trim().is_empty() { base = "Sheet".into(); }
    if used.insert(base.clone()) { return base; }
    for n in 2..99 {
        let cand = format!("{}_{}", base.chars().take(25).collect::<String>(), n);
        if used.insert(cand.clone()) { return cand; }
    }
    "Sheet_Extra".into()
}
''',

    "rust-core/src/lib.rs": r'''mod db;
mod importer;
mod models;
mod persian;
mod reports;

pub use models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    ImportReport, JalaliDayCell, JalaliMonthGrid, JalaliYearMonth, MonthlyClassReport,
    MonthlyStudentStat, Period, PeriodSummary, PrincipalReportBundle, StudentAttendanceRow,
    TopStudentCount,
};

use rusqlite::Connection;
use std::sync::{Arc, Mutex};

uniffi::setup_scaffolding!();

#[derive(uniffi::Object)]
pub struct AttendanceEngine {
    conn: Mutex<Connection>,
}

#[uniffi::export]
impl AttendanceEngine {
    #[uniffi::constructor]
    pub fn new(db_path: String) -> Result<Arc<Self>, CoreError> {
        Ok(Arc::new(Self { conn: Mutex::new(db::init_database(&db_path)?) }))
    }

    pub fn import_file_bytes(&self, file_name: String, bytes: Vec<u8>, replace_existing: bool) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        importer::import_file_bytes(&mut conn, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_classes(&conn)
    }

    pub fn get_class_attendance(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, search_query: String) -> Result<ClassAttendanceSnapshot, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_attendance(&conn, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(&self, student_id: i64, date_iso: String, period: Period, status: AttendanceStatus, note: String, teacher_name: String, lesson_name: String, class_time: String) -> Result<(), CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_attendance(&mut conn, student_id, &date_iso, period, status, &note, &teacher_name, &lesson_name, &class_time)
    }

    pub fn set_student_score(&self, student_id: i64, date_iso: String, period: Period, class_score: String, session_score: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_student_score(&conn, student_id, &date_iso, period, &class_score, &session_score)
    }

    pub fn mark_class_status(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher_name: String, lesson_name: String, class_time: String) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::mark_class_status(&conn, &major, &grade, section, &date_iso, period, status, only_unmarked, &teacher_name, &lesson_name, &class_time)
    }

    pub fn copy_from_previous_period(&self, major: String, grade: String, section: i32, date_iso: String, target_period: Period) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::copy_from_previous_period(&conn, &major, &grade, section, &date_iso, target_period)
    }

    pub fn add_student(&self, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String, class_score: String) -> Result<i64, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::add_student(&conn, &school_name, &major, &grade, section, &first_name, &last_name, &father_name, &national_id, &mobile, &class_score)
    }

    pub fn update_student(&self, student_id: i64, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String, class_score: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::update_student(&conn, student_id, &first_name, &last_name, &father_name, &national_id, &mobile, &class_score)
    }

    pub fn delete_student(&self, student_id: i64) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_student(&conn, student_id)
    }

    pub fn delete_class(&self, major: String, grade: String, section: i32) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_class(&conn, &major, &grade, section)
    }

    pub fn get_backup_stats(&self) -> Result<BackupStats, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_backup_stats(&conn)
    }

    pub fn get_class_analytics(&self, major: String, grade: String, section: i32) -> Result<ClassAnalytics, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_analytics(&conn, &major, &grade, section)
    }

    pub fn generate_period_group_message(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, target_status: AttendanceStatus, teacher_name: String, lesson_name: String, whole_school: bool) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::generate_period_group_message(&conn, &major, &grade, section, &date_iso, period, target_status, &teacher_name, &lesson_name, whole_school)
    }

    pub fn generate_principal_report(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool, teacher_name: String) -> Result<PrincipalReportBundle, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        if whole_school {
            reports::generate_principal_report(&conn, None, None, None, &date_iso, &teacher_name)
        } else {
            reports::generate_principal_report(&conn, Some(&major), Some(&grade), Some(section), &date_iso, &teacher_name)
        }
    }

    pub fn export_daily_csv(&self, major: String, grade: String, section: i32, date_iso: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_daily_csv(&conn, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_daily_xlsx(&conn, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn get_monthly_report(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let rep = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&rep, &major, &grade, section)
    }

    pub fn export_monthly_csv(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let rep = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&rep, &major, &grade, section))
    }

    pub fn export_template_xlsx(&self) -> Result<Vec<u8>, CoreError> { reports::export_template_xlsx() }

    pub fn export_backup_json(&self) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::export_backup_json(&conn)
    }

    pub fn restore_backup_json(&self, json_text: String) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::restore_backup_json(&mut conn, &json_text)
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
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_setting(&conn, &key, &value)
    }

    pub fn get_setting(&self, key: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_setting(&conn, &key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = "ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل\n\
1,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544\n\
2,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,1,مهدی,بهروزی,بهرام,5150303194,9172893258\n";

    #[test]
    fn test_v3_sms_labels_scores_and_backup() {
        let eng = AttendanceEngine::new(":memory:".into()).unwrap();
        eng.import_file_bytes("s.csv".into(), SAMPLE.as_bytes().to_vec(), true).unwrap();
        let snap = eng.get_class_attendance("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        let (s1, s2) = (snap.students[0].student_id, snap.students[1].student_id);

        eng.set_student_score(s1, "2025-10-12".into(), Period::First, "19.5".into(), "20".into()).unwrap();
        for p in [Period::First, Period::Second, Period::Third, Period::Fourth] {
            eng.set_attendance(s1, "2025-10-12".into(), p, AttendanceStatus::Absent, "".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
            eng.set_attendance(s2, "2025-10-12".into(), p, if p == Period::First { AttendanceStatus::Late } else { AttendanceStatus::Present }, "".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        }
        let pr = eng.generate_principal_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), false, "دبیر".into()).unwrap();
        assert_eq!(pr.sms_text.matches("محمد آزادی").count(), 1);
        assert!(pr.sms_text.contains("(غایب)"));
        assert!(pr.sms_text.contains("(تأخیر)"));
        assert!(pr.sms_text.contains("حاضر"));

        let backup = eng.export_backup_json().unwrap();
        assert!(backup.contains("19.5"));
        let eng2 = AttendanceEngine::new(":memory:".into()).unwrap();
        eng2.restore_backup_json(backup).unwrap();
        assert_eq!(eng2.get_backup_stats().unwrap().scores_count, 2);
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
    print(f"\nPart 1 (Rust Core v3.0) done: {len(FILES)} files.")


if __name__ == "__main__":
    main()
