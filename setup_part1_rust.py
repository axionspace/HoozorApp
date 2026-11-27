from pathlib import Path

FILES = {
    "rust-core/Cargo.toml": r'''[package]
name = "hozoor_core"
version = "2.0.0"
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
            AttendanceStatus::Unmarked => "ثبت‌نشده",
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
    input
        .chars()
        .map(|c| match c {
            '0' => '۰',
            '1' => '۱',
            '2' => '۲',
            '3' => '۳',
            '4' => '۴',
            '5' => '۵',
            '6' => '۶',
            '7' => '۷',
            '8' => '۸',
            '9' => '۹',
            _ => c,
        })
        .collect()
}

pub fn persian_sort_key(input: &str) -> Vec<u8> {
    normalize_persian(input)
        .chars()
        .map(|c| match c {
            ' ' | '\u{200C}' => 1,
            'آ' => 2,
            'ا' => 3,
            'ب' => 4,
            'پ' => 5,
            'ت' => 6,
            'ث' => 7,
            'ج' => 8,
            'چ' => 9,
            'ح' => 10,
            'خ' => 11,
            'د' => 12,
            'ذ' => 13,
            'ر' => 14,
            'ز' => 15,
            'ژ' => 16,
            'س' => 17,
            'ش' => 18,
            'ص' => 19,
            'ض' => 20,
            'ط' => 21,
            'ظ' => 22,
            'ع' => 23,
            'غ' => 24,
            'ف' => 25,
            'ق' => 26,
            'ک' => 27,
            'گ' => 28,
            'ل' => 29,
            'م' => 30,
            'ن' => 31,
            'و' => 32,
            'ه' => 33,
            'ی' | 'ئ' => 34,
            '0'..='9' => 40 + (c as u8 - b'0'),
            _ => 100,
        })
        .collect()
}

pub fn normalize_national_id(raw: &str) -> String {
    let digits: String = normalize_persian(raw)
        .chars()
        .filter(|c| c.is_ascii_digit())
        .collect();
    if digits.is_empty() {
        return String::new();
    }
    if digits.len() < 10 {
        format!("{:0>10}", digits)
    } else {
        digits.chars().take(10).collect()
    }
}

pub fn normalize_mobile(raw: &str) -> String {
    let digits: String = normalize_persian(raw)
        .chars()
        .filter(|c| c.is_ascii_digit())
        .collect();
    if digits.len() == 10 && digits.starts_with('9') {
        format!("0{digits}")
    } else if digits.len() == 12 && digits.starts_with("98") {
        format!("0{}", &digits[2..])
    } else {
        digits
    }
}

pub fn grade_rank(grade: &str) -> i32 {
    match normalize_persian(grade).as_str() {
        "اول" => 1,
        "دوم" => 2,
        "سوم" => 3,
        "چهارم" => 4,
        "پنجم" => 5,
        "ششم" => 6,
        "هفتم" => 7,
        "هشتم" => 8,
        "نهم" => 9,
        "دهم" => 10,
        "یازدهم" => 11,
        "دوازدهم" => 12,
        _ => 99,
    }
}

pub fn is_middle_grade(grade: &str) -> bool {
    matches!(normalize_persian(grade).as_str(), "هفتم" | "هشتم" | "نهم")
}

pub fn format_iso_to_jalali(date_iso: &str) -> String {
    let parts: Vec<&str> = date_iso.split('-').collect();
    if parts.len() != 3 {
        return to_persian_digits(date_iso);
    }
    let (Ok(gy), Ok(gm), Ok(gd)) = (
        parts[0].parse::<i32>(),
        parts[1].parse::<u32>(),
        parts[2].parse::<u32>(),
    ) else {
        return to_persian_digits(date_iso);
    };
    if !(1..=12).contains(&gm) || !(1..=31).contains(&gd) {
        return to_persian_digits(date_iso);
    }
    let (jy, jm, jd) = gregorian_to_jalali(gy, gm, gd);
    let weekday = weekday_fa(gy, gm, gd);
    let month = month_name_fa(jm);
    to_persian_digits(&format!("{weekday} {jd} {month} {jy}"))
}

pub fn format_iso_to_jalali_short(date_iso: &str) -> String {
    let parts: Vec<&str> = date_iso.split('-').collect();
    if parts.len() == 3 {
        if let (Ok(gy), Ok(gm), Ok(gd)) = (
            parts[0].parse::<i32>(),
            parts[1].parse::<u32>(),
            parts[2].parse::<u32>(),
        ) {
            let (jy, jm, jd) = gregorian_to_jalali(gy, gm, gd);
            return to_persian_digits(&format!("{jd} {} {jy}", month_name_fa(jm)));
        }
    }
    to_persian_digits(date_iso)
}

pub fn iso_to_jalali_year_month(date_iso: &str) -> (i32, u32) {
    let parts: Vec<&str> = date_iso.split('-').collect();
    if parts.len() == 3 {
        if let (Ok(gy), Ok(gm), Ok(gd)) = (
            parts[0].parse::<i32>(),
            parts[1].parse::<u32>(),
            parts[2].parse::<u32>(),
        ) {
            let (jy, jm, _) = gregorian_to_jalali(gy, gm, gd);
            return (jy, jm);
        }
    }
    (1404, 7)
}

pub fn gregorian_to_jalali(gy: i32, gm: u32, gd: u32) -> (i32, u32, u32) {
    let g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
    let gy2 = if gm > 2 { gy + 1 } else { gy };
    let mut days = 355666
        + (365 * gy)
        + ((gy2 + 3) / 4)
        - ((gy2 + 99) / 100)
        + ((gy2 + 399) / 400)
        + gd as i32
        + g_d_m[(gm - 1) as usize];
    let mut jy = -1595 + (33 * (days / 12053));
    days %= 12053;
    jy += 4 * (days / 1461);
    days %= 1461;
    if days > 365 {
        jy += (days - 1) / 365;
        days = (days - 1) % 365;
    }
    let (jm, jd) = if days < 186 {
        (1 + (days / 31) as u32, 1 + (days % 31) as u32)
    } else {
        (7 + ((days - 186) / 30) as u32, 1 + ((days - 186) % 30) as u32)
    };
    (jy, jm, jd)
}

pub fn jalali_to_gregorian(jy: i32, jm: u32, jd: u32) -> (i32, u32, u32) {
    let jy2 = jy + 1595;
    let mut days = -355668
        + (365 * jy2)
        + ((jy2 / 33) * 8)
        + (((jy2 % 33) + 3) / 4)
        + jd as i32
        + if jm < 7 {
            (jm as i32 - 1) * 31
        } else {
            ((jm as i32 - 7) * 30) + 186
        };
    let mut gy = 400 * (days / 146097);
    days %= 146097;
    if days > 36524 {
        days -= 1;
        gy += 100 * (days / 36524);
        days %= 36524;
        if days >= 365 {
            days += 1;
        }
    }
    gy += 4 * (days / 1461);
    days %= 1461;
    if days > 365 {
        gy += (days - 1) / 365;
        days = (days - 1) % 365;
    }
    let mut gd = days + 1;
    let is_leap = (gy % 4 == 0 && gy % 100 != 0) || (gy % 400 == 0);
    let sal_a = [0, 31, if is_leap { 29 } else { 28 }, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    let mut gm = 1u32;
    while gm <= 12 && gd > sal_a[gm as usize] {
        gd -= sal_a[gm as usize];
        gm += 1;
    }
    (gy, gm, gd as u32)
}

pub fn jalali_month_days(jy: i32, jm: u32) -> u32 {
    match jm {
        1..=6 => 31,
        7..=11 => 30,
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
        let fa_wd = (sunday_based_weekday(gy, gm, gd) + 1) % 7;
        days.push(JalaliDayCell {
            day: d as i32,
            date_iso: format!("{gy:04}-{gm:02}-{gd:02}"),
            is_friday: fa_wd == 6,
        });
    }

    JalaliMonthGrid {
        year: jy,
        month: jm as i32,
        month_label: format_jalali_month_label(jy, jm),
        leading_blanks: first_fa_wd as i32,
        days,
    }
}

fn sunday_based_weekday(y: i32, m: u32, d: u32) -> usize {
    let t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4];
    let y = if m < 3 { y - 1 } else { y };
    (y + y / 4 - y / 100 + y / 400 + t[(m - 1) as usize] + d as i32).rem_euclid(7) as usize
}

fn weekday_fa(y: i32, m: u32, d: u32) -> &'static str {
    const WEEKDAYS: [&str; 7] = ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"];
    WEEKDAYS[sunday_based_weekday(y, m, d)]
}

pub fn month_name_fa(m: u32) -> &'static str {
    match m {
        1 => "فروردین",
        2 => "اردیبهشت",
        3 => "خرداد",
        4 => "تیر",
        5 => "مرداد",
        6 => "شهریور",
        7 => "مهر",
        8 => "آبان",
        9 => "آذر",
        10 => "دی",
        11 => "بهمن",
        12 => "اسفند",
        _ => "",
    }
}
''',

    "rust-core/src/importer.rs": r'''use crate::models::{CoreError, ImportReport};
use crate::persian::{is_middle_grade, normalize_mobile, normalize_national_id, normalize_persian};
use calamine::{open_workbook_auto_from_rs, Data, Reader};
use rusqlite::{params, Connection};
use std::io::Cursor;

struct ParsedStudent {
    row_num: i32,
    school_name: String,
    major: String,
    grade: String,
    section: i32,
    first_name: String,
    last_name: String,
    father_name: String,
    national_id: String,
    mobile: String,
    search_key: String,
}

pub fn import_file_bytes(
    conn: &mut Connection,
    file_name: &str,
    bytes: &[u8],
    replace_existing: bool,
) -> Result<ImportReport, CoreError> {
    if bytes.is_empty() {
        return Err(CoreError::Import("فایل انتخاب‌شده خالی است".into()));
    }
    let lower_name = file_name.to_lowercase();
    let is_zip_xlsx = bytes.len() >= 4 && &bytes[0..4] == b"PK\x03\x04";
    let is_ole_xls = bytes.len() >= 4 && &bytes[0..4] == b"\xD0\xCF\x11\xE0";

    if is_zip_xlsx || is_ole_xls || lower_name.ends_with(".xlsx") || lower_name.ends_with(".xls") {
        import_excel_bytes(conn, bytes, replace_existing)
    } else {
        let text = String::from_utf8(bytes.to_vec()).map_err(|_| {
            CoreError::Import("کدگذاری فایل CSV معتبر نیست؛ لطفاً با UTF-8 یا اکسل (.xlsx) ذخیره کنید".into())
        })?;
        import_csv_text(conn, &text, replace_existing)
    }
}

fn import_excel_bytes(conn: &mut Connection, bytes: &[u8], replace_existing: bool) -> Result<ImportReport, CoreError> {
    let cursor = Cursor::new(bytes);
    let mut workbook = open_workbook_auto_from_rs(cursor)
        .map_err(|e| CoreError::Import(format!("فایل اکسل قابل خواندن نیست: {e}")))?;

    let sheet_names = workbook.sheet_names().to_vec();
    let target_sheet = sheet_names
        .iter()
        .find(|name| name.contains("دانش") || name.contains("آموز"))
        .cloned()
        .or_else(|| sheet_names.into_iter().next())
        .ok_or_else(|| CoreError::Import("فایل اکسل هیچ شیتی ندارد".into()))?;

    let range = workbook
        .worksheet_range(&target_sheet)
        .map_err(|e| CoreError::Import(format!("خطا در خواندن شیت '{target_sheet}': {e}")))?;

    let mut rows_vec: Vec<Vec<String>> = Vec::with_capacity(range.height());
    for row in range.rows() {
        rows_vec.push(row.iter().map(cell_to_string).collect());
    }
    persist_rows(conn, &rows_vec, replace_existing)
}

fn import_csv_text(conn: &mut Connection, csv_text: &str, replace_existing: bool) -> Result<ImportReport, CoreError> {
    let cleaned = csv_text.trim_start_matches('\u{FEFF}');
    let first_non_empty = cleaned
        .lines()
        .find(|l| !l.trim().is_empty())
        .ok_or_else(|| CoreError::Import("فایل CSV خالی است".into()))?;

    let delimiter = detect_csv_delimiter(first_non_empty);
    let mut rows_vec = Vec::new();
    for line in cleaned.lines() {
        if !line.trim().is_empty() {
            rows_vec.push(parse_csv_line(line, delimiter));
        }
    }
    persist_rows(conn, &rows_vec, replace_existing)
}

fn detect_csv_delimiter(sample: &str) -> char {
    let commas = sample.matches(',').count();
    let semicolons = sample.matches(';').count();
    let tabs = sample.matches('\t').count();
    if semicolons > commas && semicolons >= tabs { ';' }
    else if tabs > commas && tabs > semicolons { '\t' }
    else { ',' }
}

fn parse_csv_line(line: &str, delimiter: char) -> Vec<String> {
    let mut fields = Vec::with_capacity(10);
    let mut current = String::new();
    let mut in_quotes = false;
    let mut chars = line.chars().peekable();
    while let Some(c) = chars.next() {
        if in_quotes {
            if c == '"' {
                if chars.peek() == Some(&'"') { chars.next(); current.push('"'); }
                else { in_quotes = false; }
            } else { current.push(c); }
        } else if c == '"' {
            in_quotes = true;
        } else if c == delimiter {
            fields.push(current.trim().to_string());
            current.clear();
        } else {
            current.push(c);
        }
    }
    fields.push(current.trim().to_string());
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
    if raw_rows.is_empty() {
        return Err(CoreError::Import("فایل خالی است".into()));
    }
    let first_norm: Vec<String> = raw_rows[0].iter().map(|c| normalize_persian(c)).collect();
    let has_header = first_norm.iter().any(|c| c.contains("ردیف") || c.contains("نام خانوادگی") || c.contains("کد ملی"));
    let start_idx = if has_header { 1 } else { 0 };

    let mut students = Vec::with_capacity(raw_rows.len());
    let mut skipped = 0i32;

    for (idx, cols) in raw_rows[start_idx..].iter().enumerate() {
        if cols.len() < 9 { skipped += 1; continue; }
        let row_num = normalize_persian(&cols[0]).parse::<i32>().unwrap_or((idx + 1) as i32);
        let school_name = {
            let s = cols[1].trim();
            if s.is_empty() { "مدرسه".to_string() } else { s.to_string() }
        };
        let grade = cols[3].trim().to_string();
        let major = if is_middle_grade(&grade) { String::new() } else { cols[2].trim().to_string() };
        let section = normalize_persian(&cols[4]).parse::<i32>().unwrap_or(1).max(1);
        let first_name = cols[5].trim().to_string();
        let last_name = cols[6].trim().to_string();
        let father_name = cols[7].trim().to_string();
        let national_id = normalize_national_id(&cols[8]);
        let mobile = cols.get(9).map(|m| normalize_mobile(m)).unwrap_or_default();

        if first_name.is_empty() || last_name.is_empty() || grade.is_empty() || national_id.is_empty() {
            skipped += 1;
            continue;
        }
        let search_key = normalize_persian(&format!("{first_name} {last_name} {father_name} {national_id} {mobile}"));
        students.push(ParsedStudent {
            row_num, school_name, major, grade, section,
            first_name, last_name, father_name, national_id, mobile, search_key,
        });
    }

    if students.is_empty() {
        return Err(CoreError::Import("هیچ دانش‌آموز معتبری در فایل یافت نشد".into()));
    }

    let tx = conn.transaction().map_err(|e| CoreError::Database(e.to_string()))?;
    if replace_existing {
        tx.execute("DELETE FROM students", []).map_err(|e| CoreError::Database(e.to_string()))?;
    }

    {
        let mut stmt = tx
            .prepare_cached(
                "INSERT INTO students (
                    row_num, school_name, major, grade, section,
                    first_name, last_name, father_name, national_id, mobile, search_key
                ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)
                ON CONFLICT(school_name, national_id) DO UPDATE SET
                    row_num = excluded.row_num,
                    major = excluded.major,
                    grade = excluded.grade,
                    section = excluded.section,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    father_name = excluded.father_name,
                    mobile = excluded.mobile,
                    search_key = excluded.search_key",
            )
            .map_err(|e| CoreError::Database(e.to_string()))?;

        for s in &students {
            stmt.execute(params![
                s.row_num, s.school_name, s.major, s.grade, s.section,
                s.first_name, s.last_name, s.father_name, s.national_id, s.mobile, s.search_key,
            ])
            .map_err(|e| CoreError::Database(e.to_string()))?;
        }
    }

    let classes_count: i32 = tx
        .query_row("SELECT COUNT(*) FROM (SELECT DISTINCT school_name, major, grade, section FROM students)", [], |r| r.get(0))
        .map_err(|e| CoreError::Database(e.to_string()))?;
    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;

    Ok(ImportReport { imported_count: students.len() as i32, skipped_count: skipped, classes_count })
}
''',

    "rust-core/src/db.rs": r'''use crate::models::{
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
''',

    "rust-core/src/reports.rs": r'''use crate::db;
use crate::models::{
    AttendanceStatus, ClassGroup, CoreError, MonthlyClassReport, Period, PrincipalReportBundle,
};
use crate::persian::{format_iso_to_jalali, format_iso_to_jalali_short, to_persian_digits};
use rusqlite::Connection;
use rust_xlsxwriter::{Color, Format, FormatAlign, Workbook};
use std::collections::HashSet;

const PERIOD_NAMES_FULL: [&str; 4] = ["زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
const PERIOD_NAMES_SMS: [&str; 4] = ["زنگ ۱", "زنگ ۲", "زنگ ۳", "زنگ ۴"];

fn format_class_title(major: &str, grade: &str, section: i32) -> String {
    let sec = to_persian_digits(&section.to_string());
    if major.trim().is_empty() {
        format!("پایه {grade} شعبه {sec}")
    } else {
        format!("{major} - {grade} شعبه {sec}")
    }
}

pub fn generate_period_group_message(
    conn: &Connection,
    school_name: &str,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
    period: Period,
    target_status: AttendanceStatus,
    teacher_name: &str,
    lesson_name: &str,
) -> Result<String, CoreError> {
    let snap = db::get_class_attendance(conn, school_name, major, grade, section, date_iso, period, "")?;
    let matched: Vec<_> = snap.students.into_iter().filter(|s| s.current_status == target_status).collect();
    if matched.is_empty() {
        let word = if target_status == AttendanceStatus::Late { "تأخیری" } else { "غایبی" };
        return Err(CoreError::InvalidInput(format!("در این زنگ هیچ دانش‌آموز {word} ثبت نشده است")));
    }

    let action_text = if target_status == AttendanceStatus::Late { "با تأخیر حاضر شده‌اند" } else { "غایب بوده‌اند" };
    let cls_title = format_class_title(major, grade, section);
    let lesson_part = if lesson_name.trim().is_empty() { String::new() } else { format!("در درس {} ", lesson_name.trim()) };
    let jalali = format_iso_to_jalali_short(date_iso);

    let mut msg = format!(
        "سلام علیکم\nمدیریت محترم {school_name}،\nدانش‌آموزان زیر {lesson_part}{cls_title}، {} مورخه {jalali} {action_text}:\n\n",
        period.label_fa()
    );
    for (i, s) in matched.iter().enumerate() {
        let num = to_persian_digits(&(i + 1).to_string());
        let father = if s.father_name.is_empty() { "ثبت نشده" } else { &s.father_name };
        msg.push_str(&format!("{num}. {} {}، فرزند {father}\n", s.first_name, s.last_name));
    }
    if !teacher_name.trim().is_empty() {
        msg.push_str(&format!("\nبا تشکر\n{}", teacher_name.trim()));
    }
    Ok(msg.trim().to_string())
}

pub fn generate_principal_report(
    conn: &Connection,
    school_name: &str,
    major: Option<&str>,
    grade: Option<&str>,
    section: Option<i32>,
    date_iso: &str,
    teacher_name: &str,
) -> Result<PrincipalReportBundle, CoreError> {
    let all = db::get_classes(conn)?;
    let classes: Vec<ClassGroup> = match (major, grade, section) {
        (Some(m), Some(g), Some(sec)) => all.into_iter().filter(|c| c.school_name == school_name && c.major == m && c.grade == g && c.section == sec).collect(),
        _ => all.into_iter().filter(|c| school_name.is_empty() || c.school_name == school_name).collect(),
    };
    if classes.is_empty() {
        return Err(CoreError::InvalidInput("هیچ کلاسی یافت نشد".into()));
    }

    let jalali_full = format_iso_to_jalali(date_iso);
    let jalali_short = format_iso_to_jalali_short(date_iso);
    let active_school = &classes[0].school_name;
    let is_whole_school = classes.len() > 1;

    let mut full = String::with_capacity(1024);
    let mut sms = String::with_capacity(512);
    full.push_str(&format!("📋 گزارش حضور و غیاب {active_school}\n📅 تاریخ: {jalali_full}\n"));
    if !teacher_name.trim().is_empty() {
        full.push_str(&format!("👤 دبیر: {}\n", teacher_name.trim()));
    }
    if is_whole_school {
        sms.push_str(&format!("گزارش {active_school} - {jalali_short}\n"));
    } else {
        let c = &classes[0];
        let cls_title = format_class_title(&c.major, &c.grade, c.section);
        full.push_str(&format!("🏫 کلاس: {cls_title}\n"));
        sms.push_str(&format!("گزارش {cls_title} - {jalali_short}\n"));
    }

    let (mut total_full_day, mut total_partial, mut total_late) = (0, 0, 0);
    let mut any_class_had_data = false;

    for cls in &classes {
        let snap = db::get_class_attendance(conn, &cls.school_name, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?;
        let active_periods: Vec<usize> = (0..4)
            .filter(|&p| snap.students.iter().any(|s| s.period_statuses[p] != AttendanceStatus::Unmarked))
            .collect();
        if active_periods.is_empty() { continue; }
        any_class_had_data = true;

        let mut full_day_ids: HashSet<i64> = HashSet::new();
        let mut full_day_names: Vec<String> = Vec::new();
        if active_periods.len() >= 2 {
            for s in &snap.students {
                let all_abs_or_exc = active_periods.iter().all(|&p| matches!(s.period_statuses[p], AttendanceStatus::Absent | AttendanceStatus::Excused));
                if all_abs_or_exc {
                    full_day_ids.insert(s.student_id);
                    let all_exc = active_periods.iter().all(|&p| s.period_statuses[p] == AttendanceStatus::Excused);
                    full_day_names.push(if all_exc { format!("{} {} (موجه)", s.first_name, s.last_name) } else { format!("{} {}", s.first_name, s.last_name) });
                }
            }
        }

        let mut per_period_entries: Vec<(usize, Vec<String>, Vec<String>)> = Vec::new();
        let mut class_has_issue = !full_day_names.is_empty();

        for &p in &active_periods {
            let (mut full_items, mut sms_items) = (Vec::new(), Vec::new());
            for s in &snap.students {
                if full_day_ids.contains(&s.student_id) { continue; }
                match s.period_statuses[p] {
                    AttendanceStatus::Absent => { total_partial += 1; class_has_issue = true; full_items.push(format!("{} {} (غایب)", s.first_name, s.last_name)); sms_items.push(format!("{} {}", s.first_name, s.last_name)); }
                    AttendanceStatus::Excused => { total_partial += 1; class_has_issue = true; full_items.push(format!("{} {} (موجه)", s.first_name, s.last_name)); sms_items.push(format!("{} {}(موجه)", s.first_name, s.last_name)); }
                    AttendanceStatus::Late => { total_late += 1; class_has_issue = true; full_items.push(format!("{} {} (تأخیر)", s.first_name, s.last_name)); sms_items.push(format!("{} {}(تأخیر)", s.first_name, s.last_name)); }
                    _ => {}
                }
            }
            per_period_entries.push((p, full_items, sms_items));
        }

        total_full_day += full_day_names.len() as i32;
        if is_whole_school {
            if !class_has_issue { continue; }
            let hdr = format_class_title(&cls.major, &cls.grade, cls.section);
            full.push_str(&format!("\n────────────\n🏫 {hdr}\n"));
            sms.push_str(&format!("\n[{hdr}]\n"));
        } else {
            full.push_str("────────────────────\n");
        }

        if !class_has_issue {
            full.push_str("✅ همه دانش‌آموزان در زنگ‌های ثبت‌شده حاضر بودند.\n");
            sms.push_str("همه دانش‌آموزان حاضر بودند.\n");
            continue;
        }
        if !full_day_names.is_empty() {
            let cnt = to_persian_digits(&full_day_names.len().to_string());
            full.push_str(&format!("🔴 غایبین کل روز ({cnt} نفر):\n"));
            for name in &full_day_names { full.push_str(&format!("• {name}\n")); }
            sms.push_str(&format!("کل روز: {}\n", full_day_names.join("، ")));
        }
        for (p, full_items, sms_items) in per_period_entries {
            if full_items.is_empty() {
                if !is_whole_school {
                    full.push_str(&format!("\n🔔 {}:\n• بدون غیبت/تأخیر جدید\n", PERIOD_NAMES_FULL[p]));
                }
            } else {
                full.push_str(&format!("\n🔔 {}:\n", PERIOD_NAMES_FULL[p]));
                for item in &full_items { full.push_str(&format!("• {item}\n")); }
                sms.push_str(&format!("{}: {}\n", PERIOD_NAMES_SMS[p], sms_items.join("، ")));
            }
        }
    }

    if !any_class_had_data {
        full.push_str("\nهنوز هیچ حضور و غیابی برای این تاریخ ثبت نشده است.");
        sms.push_str("حضور و غیابی ثبت نشده است.");
    } else if is_whole_school && total_full_day == 0 && total_partial == 0 && total_late == 0 {
        full.push_str("\n✅ امروز در تمام کلاس‌های ثبت‌شده، همه دانش‌آموزان حاضر بودند.");
        sms.push_str("همه دانش‌آموزان کل مدرسه حاضر بودند.");
    }

    Ok(PrincipalReportBundle {
        full_text: full.trim().to_string(),
        sms_text: sms.trim().to_string(),
        full_day_absent_count: total_full_day,
        partial_absent_count: total_partial,
        late_count: total_late,
    })
}

pub fn export_daily_csv(conn: &Connection, school_name: &str, major: &str, grade: &str, section: i32, date_iso: &str) -> Result<String, CoreError> {
    let snap = db::get_class_attendance(conn, school_name, major, grade, section, date_iso, Period::First, "")?;
    let mut csv = String::with_capacity(snap.students.len() * 140 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل,تاریخ,زنگ اول,زنگ دوم,زنگ سوم,زنگ چهارم\n");
    for (idx, s) in snap.students.iter().enumerate() {
        csv.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
            idx + 1, school_name, major, grade, section, s.first_name, s.last_name, s.father_name,
            s.national_id, s.mobile, snap.jalali_date,
            s.period_statuses[0].label_fa(), s.period_statuses[1].label_fa(),
            s.period_statuses[2].label_fa(), s.period_statuses[3].label_fa(),
        ));
    }
    Ok(csv)
}

pub fn export_daily_xlsx(conn: &Connection, school_name: &str, major: &str, grade: &str, section: i32, date_iso: &str, all_classes: bool) -> Result<Vec<u8>, CoreError> {
    let all = db::get_classes(conn)?;
    let classes: Vec<ClassGroup> = if all_classes {
        all.into_iter().filter(|c| school_name.is_empty() || c.school_name == school_name).collect()
    } else {
        all.into_iter().filter(|c| c.school_name == school_name && c.major == major && c.grade == grade && c.section == section).collect()
    };
    if classes.is_empty() {
        return Err(CoreError::InvalidInput("هیچ کلاسی برای خروجی وجود ندارد".into()));
    }

    let mut workbook = Workbook::new();
    let header_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x1B5E20)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cell_fmt = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    let present_fmt = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xD7F5E6)).set_font_color(Color::RGB(0x1B5E20)).set_align(FormatAlign::Center);
    let absent_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFDADF)).set_font_color(Color::RGB(0xB71C1C)).set_align(FormatAlign::Center);
    let late_fmt = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFECC7)).set_font_color(Color::RGB(0x9A5B00)).set_align(FormatAlign::Center);
    let excused_fmt = Format::new().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xDCE7FF)).set_font_color(Color::RGB(0x1A47A6)).set_align(FormatAlign::Center);

    let headers = ["ردیف", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل", "تاریخ", "زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
    let mut used_names = HashSet::new();

    for cls in classes {
        let snap = db::get_class_attendance(conn, &cls.school_name, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?;
        let sheet = workbook.add_worksheet();
        let raw_title = if cls.major.is_empty() { format!("{} {}", cls.grade, cls.section) } else { format!("{} {} {}", cls.major, cls.grade, cls.section) };
        let sheet_name = unique_sheet_name(&raw_title, &mut used_names);
        sheet.set_name(&sheet_name).map_err(|e| CoreError::Import(e.to_string()))?;
        sheet.set_right_to_left(true);

        for (col, h) in headers.iter().enumerate() {
            let _ = sheet.write_string_with_format(0, col as u16, *h, &header_fmt);
        }
        for (idx, s) in snap.students.iter().enumerate() {
            let r = (idx + 1) as u32;
            let _ = sheet.write_number_with_format(r, 0, (idx + 1) as f64, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 1, &s.first_name, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 2, &s.last_name, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 3, &s.father_name, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 4, &s.national_id, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 5, &s.mobile, &cell_fmt);
            let _ = sheet.write_string_with_format(r, 6, &snap.jalali_date, &cell_fmt);
            for p in 0..4 {
                let st = s.period_statuses[p];
                let fmt = match st {
                    AttendanceStatus::Present => &present_fmt,
                    AttendanceStatus::Absent => &absent_fmt,
                    AttendanceStatus::Late => &late_fmt,
                    AttendanceStatus::Excused => &excused_fmt,
                    AttendanceStatus::Unmarked => &cell_fmt,
                };
                let _ = sheet.write_string_with_format(r, (7 + p) as u16, st.label_fa(), fmt);
            }
        }
        sheet.autofit();
    }
    workbook.save_to_buffer().map_err(|e| CoreError::Import(format!("خطا در ساخت فایل اکسل: {e}")))
}

pub fn export_monthly_xlsx(report: &MonthlyClassReport, major: &str, grade: &str, section: i32) -> Result<Vec<u8>, CoreError> {
    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();
    let mut used = HashSet::new();
    let name = unique_sheet_name(&format!("ماهانه {}", report.month_label), &mut used);
    sheet.set_name(&name).map_err(|e| CoreError::Import(e.to_string()))?;
    sheet.set_right_to_left(true);

    let header_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x0D47A1)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cell_fmt = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    let warn_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFDADF)).set_font_color(Color::RGB(0xB71C1C)).set_align(FormatAlign::Center);

    let headers = ["ردیف", "کلاس", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل", "زنگ حاضر", "زنگ غایب", "غیبت کل روز", "تأخیر", "موجه", "درصد حضور"];
    for (col, h) in headers.iter().enumerate() { let _ = sheet.write_string_with_format(0, col as u16, *h, &header_fmt); }

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
        let _ = sheet.write_number_with_format(r, 7, s.present_periods as f64, &cell_fmt);
        let abs_fmt = if s.absent_periods > 0 { &warn_fmt } else { &cell_fmt };
        let _ = sheet.write_number_with_format(r, 8, s.absent_periods as f64, abs_fmt);
        let _ = sheet.write_number_with_format(r, 9, s.full_absent_days as f64, abs_fmt);
        let _ = sheet.write_number_with_format(r, 10, s.late_periods as f64, &cell_fmt);
        let _ = sheet.write_number_with_format(r, 11, s.excused_periods as f64, &cell_fmt);
        let _ = sheet.write_string_with_format(r, 12, &format!("{}٪", to_persian_digits(&format!("{:.1}", s.attendance_percent))), &cell_fmt);
    }
    sheet.autofit();
    workbook.save_to_buffer().map_err(|e| CoreError::Import(format!("خطا در ساخت اکسل ماهانه: {e}")))
}

pub fn export_monthly_csv(report: &MonthlyClassReport, school_name: &str, major: &str, grade: &str, section: i32) -> String {
    let mut csv = String::with_capacity(report.students.len() * 120 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,ماه,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل,زنگ حاضر,زنگ غایب,غیبت کل روز,تأخیر,موجه,درصد حضور\n");
    for (idx, s) in report.students.iter().enumerate() {
        csv.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.1}%\n",
            idx + 1, report.month_label, school_name, major, grade, section,
            s.first_name, s.last_name, s.father_name, s.national_id, s.mobile,
            s.present_periods, s.absent_periods, s.full_absent_days,
            s.late_periods, s.excused_periods, s.attendance_percent
        ));
    }
    csv
}

pub fn export_template_xlsx() -> Result<Vec<u8>, CoreError> {
    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();
    sheet.set_name("دانش‌آموزان").map_err(|e| CoreError::Import(e.to_string()))?;
    sheet.set_right_to_left(true);

    let header_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x145548)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cell_fmt = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);

    let headers = ["ردیف", "نام مدرسه", "رشته", "پایه", "شعبه", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل"];
    for (c, h) in headers.iter().enumerate() { let _ = sheet.write_string_with_format(0, c as u16, *h, &header_fmt); }

    let sample = [
        ["1", "دبیرستان نمونه", "تجربی", "دهم", "1", "علی", "احمدی", "حسن", "1000000001", "09121234561"],
        ["2", "دبیرستان نمونه", "تجربی", "دهم", "1", "رضا", "محمدی", "مهدی", "1000000002", "09121234562"],
        ["3", "دبیرستان نمونه", "ریاضی", "یازدهم", "1", "امیر", "کریمی", "سعید", "1000000003", "09121234563"],
        ["4", "دبیرستان متوسطه اول", "", "هفتم", "1", "پارسا", "رحیمی", "جواد", "1000000004", "09121234564"],
    ];
    for (r_idx, row) in sample.iter().enumerate() {
        for (c_idx, val) in row.iter().enumerate() {
            let _ = sheet.write_string_with_format((r_idx + 1) as u32, c_idx as u16, *val, &cell_fmt);
        }
    }
    sheet.autofit();
    workbook.save_to_buffer().map_err(|e| CoreError::Import(format!("خطا در ساخت فایل نمونه: {e}")))
}

fn unique_sheet_name(raw: &str, used: &mut HashSet<String>) -> String {
    let sanitized: String = raw.chars().filter(|c| !matches!(c, ':' | '\\' | '/' | '?' | '*' | '[' | ']')).collect();
    let mut base: String = sanitized.chars().take(28).collect();
    if base.trim().is_empty() { base = "Sheet".into(); }
    if used.insert(base.clone()) { return base; }
    for n in 2..99 {
        let candidate = format!("{}_{}", base.chars().take(25).collect::<String>(), n);
        if used.insert(candidate.clone()) { return candidate; }
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
    AttendanceStatus, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError, ImportReport,
    JalaliDayCell, JalaliMonthGrid, JalaliYearMonth, MonthlyClassReport, MonthlyStudentStat,
    Period, PeriodSummary, PrincipalReportBundle, StudentAttendanceRow, TopStudentCount,
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
        let conn = db::init_database(&db_path)?;
        Ok(Arc::new(Self { conn: Mutex::new(conn) }))
    }

    pub fn import_file_bytes(&self, file_name: String, bytes: Vec<u8>, replace_existing: bool) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        importer::import_file_bytes(&mut conn, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_classes(&conn)
    }

    pub fn get_class_attendance(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, period: Period, search_query: String) -> Result<ClassAttendanceSnapshot, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_class_attendance(&conn, &school_name, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(&self, student_id: i64, date_iso: String, period: Period, status: AttendanceStatus, note: String, teacher_name: String, lesson_name: String, class_time: String) -> Result<(), CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_attendance(&mut conn, student_id, &date_iso, period, status, &note, &teacher_name, &lesson_name, &class_time)
    }

    pub fn mark_class_status(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher_name: String, lesson_name: String, class_time: String) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::mark_class_status(&conn, &school_name, &major, &grade, section, &date_iso, period, status, only_unmarked, &teacher_name, &lesson_name, &class_time)
    }

    pub fn copy_from_previous_period(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, target_period: Period) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::copy_from_previous_period(&conn, &school_name, &major, &grade, section, &date_iso, target_period)
    }

    pub fn add_student(&self, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<i64, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::add_student(&conn, &school_name, &major, &grade, section, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn update_student(&self, student_id: i64, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::update_student(&conn, student_id, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn delete_student(&self, student_id: i64) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::delete_student(&conn, student_id)
    }

    pub fn delete_class(&self, school_name: String, major: String, grade: String, section: i32) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::delete_class(&conn, &school_name, &major, &grade, section)
    }

    pub fn get_class_analytics(&self, school_name: String, major: String, grade: String, section: i32) -> Result<ClassAnalytics, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_class_analytics(&conn, &school_name, &major, &grade, section)
    }

    pub fn generate_period_group_message(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, period: Period, target_status: AttendanceStatus, teacher_name: String, lesson_name: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::generate_period_group_message(&conn, &school_name, &major, &grade, section, &date_iso, period, target_status, &teacher_name, &lesson_name)
    }

    pub fn generate_principal_report(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, whole_school: bool, teacher_name: String) -> Result<PrincipalReportBundle, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        if whole_school {
            reports::generate_principal_report(&conn, &school_name, None, None, None, &date_iso, &teacher_name)
        } else {
            reports::generate_principal_report(&conn, &school_name, Some(&major), Some(&grade), Some(section), &date_iso, &teacher_name)
        }
    }

    pub fn export_daily_csv(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::export_daily_csv(&conn, &school_name, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, whole_school: bool) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::export_daily_xlsx(&conn, &school_name, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn get_monthly_report(&self, school_name: String, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_monthly_report(&conn, &school_name, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(&self, school_name: String, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &school_name, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&report, &major, &grade, section)
    }

    pub fn export_monthly_csv(&self, school_name: String, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &school_name, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&report, &school_name, &major, &grade, section))
    }

    pub fn export_template_xlsx(&self) -> Result<Vec<u8>, CoreError> {
        reports::export_template_xlsx()
    }

    pub fn export_backup_json(&self) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::export_backup_json(&conn)
    }

    pub fn restore_backup_json(&self, json_text: String) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::restore_backup_json(&mut conn, &json_text)
    }

    pub fn format_jalali_date(&self, date_iso: String) -> String {
        persian::format_iso_to_jalali(&date_iso)
    }

    pub fn get_jalali_year_month(&self, date_iso: String) -> JalaliYearMonth {
        let (y, m) = persian::iso_to_jalali_year_month(&date_iso);
        JalaliYearMonth { year: y, month: m as i32, label: persian::format_jalali_month_label(y, m) }
    }

    pub fn get_jalali_month_grid(&self, jalali_year: i32, jalali_month: i32) -> JalaliMonthGrid {
        persian::build_jalali_month_grid(jalali_year, jalali_month)
    }

    pub fn set_setting(&self, key: String, value: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_setting(&conn, &key, &value)
    }

    pub fn get_setting(&self, key: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_setting(&conn, &key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_CSV: &str = "\
ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,مدرسه نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544
2,مدرسه نمونه,صنایع شیمیایی,یازدهم,1,مهدی,بهروزی,بهرام,5150303194,9172893258
3,دبیرستان متوسطه اول,,هفتم,1,پارسا,رحیمی,جواد,441746977,9124409109
";

    #[test]
    fn test_default_present_reset_all_backup_and_reports() {
        let engine = AttendanceEngine::new(":memory:".into()).unwrap();
        let rep = engine.import_file_bytes("test.csv".into(), TEST_CSV.as_bytes().to_vec(), true).unwrap();
        assert_eq!(rep.imported_count, 3);
        assert_eq!(rep.classes_count, 2);

        let snap = engine.get_class_attendance("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(snap.summary.present, 2);
        assert_eq!(snap.students[0].current_status, AttendanceStatus::Present);

        let s1 = snap.students[0].student_id;
        engine.set_attendance(s1, "2025-10-12".into(), Period::First, AttendanceStatus::Absent, "".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        let snap2 = engine.get_class_attendance("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(snap2.summary.absent, 1);

        engine.mark_class_status("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, AttendanceStatus::Present, false, "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        let snap3 = engine.get_class_attendance("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(snap3.summary.present, 2);
        assert_eq!(snap3.summary.absent, 0);

        let backup = engine.export_backup_json().unwrap();
        let engine2 = AttendanceEngine::new(":memory:".into()).unwrap();
        assert_eq!(engine2.restore_backup_json(backup).unwrap().imported_count, 3);
        assert!(engine.export_template_xlsx().unwrap().starts_with(b"PK\x03\x04"));
        assert_eq!(engine.get_jalali_month_grid(1404, 7).days.len(), 30);
    }
}
''',
}


def main():
    for rel_path, content in FILES.items():
        path = Path(rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Created: {rel_path}")
    print(f"\nPart 1 (Rust Core) done: {len(FILES)} files.")


if __name__ == "__main__":
    main()
