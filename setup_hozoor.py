import os
from pathlib import Path

FILES = {
    # ===================== RUST CORE =====================
    "rust-core/Cargo.toml": r'''[package]
name = "hozoor_core"
version = "1.1.0"
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
rust_xlsxwriter = "0.80.0"
thiserror = "2.0"

[profile.release]
opt-level = "z"
lto = true
codegen-units = 1
strip = true
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
            AttendanceStatus::Excused => "موجه",
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
''',

    "rust-core/src/persian.rs": r'''pub fn normalize_persian(input: &str) -> String {
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
        digits
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
        "دهم" => 10,
        "یازدهم" => 11,
        "دوازدهم" => 12,
        _ => 99,
    }
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

fn weekday_fa(y: i32, m: u32, d: u32) -> &'static str {
    const WEEKDAYS: [&str; 7] = ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"];
    let t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4];
    let y = if m < 3 { y - 1 } else { y };
    let idx = (y + y / 4 - y / 100 + y / 400 + t[(m - 1) as usize] + d as i32).rem_euclid(7);
    WEEKDAYS[idx as usize]
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
use crate::persian::{normalize_mobile, normalize_national_id, normalize_persian};
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
            CoreError::Import("کدگذاری فایل CSV معتبر نیست؛ لطفاً با UTF-8 یا فرمت اکسل (.xlsx) ذخیره کنید".into())
        })?;
        import_csv_text(conn, &text, replace_existing)
    }
}

pub fn import_excel_bytes(
    conn: &mut Connection,
    bytes: &[u8],
    replace_existing: bool,
) -> Result<ImportReport, CoreError> {
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

pub fn import_csv_text(
    conn: &mut Connection,
    csv_text: &str,
    replace_existing: bool,
) -> Result<ImportReport, CoreError> {
    let cleaned = csv_text.trim_start_matches('\u{FEFF}');
    let first_non_empty = cleaned
        .lines()
        .find(|l| !l.trim().is_empty())
        .ok_or_else(|| CoreError::Import("فایل CSV خالی است".into()))?;

    let delimiter = detect_csv_delimiter(first_non_empty);
    let mut rows_vec = Vec::new();
    for line in cleaned.lines() {
        if line.trim().is_empty() {
            continue;
        }
        rows_vec.push(parse_csv_line(line, delimiter));
    }
    persist_rows(conn, &rows_vec, replace_existing)
}

fn detect_csv_delimiter(sample: &str) -> char {
    let commas = sample.matches(',').count();
    let semicolons = sample.matches(';').count();
    let tabs = sample.matches('\t').count();
    if semicolons > commas && semicolons >= tabs {
        ';'
    } else if tabs > commas && tabs > semicolons {
        '\t'
    } else {
        ','
    }
}

fn parse_csv_line(line: &str, delimiter: char) -> Vec<String> {
    let mut fields = Vec::with_capacity(10);
    let mut current = String::new();
    let mut in_quotes = false;
    let mut chars = line.chars().peekable();
    while let Some(c) = chars.next() {
        if in_quotes {
            if c == '"' {
                if chars.peek() == Some(&'"') {
                    chars.next();
                    current.push('"');
                } else {
                    in_quotes = false;
                }
            } else {
                current.push(c);
            }
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
        Data::Float(f) => {
            if f.fract() == 0.0 { format!("{}", *f as i64) } else { f.to_string() }
        }
        Data::Bool(b) => b.to_string(),
        Data::DateTime(dt) => dt.as_f64().to_string(),
        _ => String::new(),
    }
}

fn persist_rows(
    conn: &mut Connection,
    raw_rows: &[Vec<String>],
    replace_existing: bool,
) -> Result<ImportReport, CoreError> {
    if raw_rows.is_empty() {
        return Err(CoreError::Import("فایل خالی است".into()));
    }

    let first_norm: Vec<String> = raw_rows[0].iter().map(|c| normalize_persian(c)).collect();
    let has_header = first_norm.iter().any(|c| {
        c.contains("ردیف") || c.contains("نام خانوادگی") || c.contains("کد ملی")
    });
    let start_idx = if has_header { 1 } else { 0 };

    let mut students = Vec::with_capacity(raw_rows.len());
    let mut skipped = 0i32;

    for (idx, cols) in raw_rows[start_idx..].iter().enumerate() {
        if cols.len() < 9 {
            skipped += 1;
            continue;
        }
        let row_num = normalize_persian(&cols[0]).parse::<i32>().unwrap_or((idx + 1) as i32);
        let school_name = cols[1].trim().to_string();
        let major = cols[2].trim().to_string();
        let grade = cols[3].trim().to_string();
        let section = normalize_persian(&cols[4]).parse::<i32>().unwrap_or(1);
        let first_name = cols[5].trim().to_string();
        let last_name = cols[6].trim().to_string();
        let father_name = cols[7].trim().to_string();
        let national_id = normalize_national_id(&cols[8]);
        let mobile = cols.get(9).map(|m| normalize_mobile(m)).unwrap_or_default();

        if first_name.is_empty() || last_name.is_empty() || national_id.is_empty() {
            skipped += 1;
            continue;
        }

        let search_key = normalize_persian(&format!(
            "{first_name} {last_name} {father_name} {national_id} {mobile}"
        ));

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
                ON CONFLICT(national_id) DO UPDATE SET
                    row_num = excluded.row_num,
                    school_name = excluded.school_name,
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
        .query_row(
            "SELECT COUNT(*) FROM (SELECT DISTINCT major, grade, section FROM students)",
            [],
            |r| r.get(0),
        )
        .map_err(|e| CoreError::Database(e.to_string()))?;

    tx.commit().map_err(|e| CoreError::Database(e.to_string()))?;

    Ok(ImportReport {
        imported_count: students.len() as i32,
        skipped_count: skipped,
        classes_count,
    })
}
''',

    "rust-core/src/db.rs": r'''use crate::models::{
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

pub fn generate_principal_report(
    conn: &Connection,
    major: Option<&str>,
    grade: Option<&str>,
    section: Option<i32>,
    date_iso: &str,
) -> Result<PrincipalReportBundle, CoreError> {
    let classes: Vec<ClassGroup> = match (major, grade, section) {
        (Some(m), Some(g), Some(sec)) if !m.is_empty() => db::get_classes(conn)?
            .into_iter()
            .filter(|c| c.major == m && c.grade == g && c.section == sec)
            .collect(),
        _ => db::get_classes(conn)?,
    };

    if classes.is_empty() {
        return Err(CoreError::InvalidInput("هیچ کلاسی یافت نشد".into()));
    }

    let jalali_full = format_iso_to_jalali(date_iso);
    let jalali_short = format_iso_to_jalali_short(date_iso);
    let school_name = &classes[0].school_name;
    let is_whole_school = classes.len() > 1;

    let mut full = String::with_capacity(1024);
    let mut sms = String::with_capacity(512);

    full.push_str(&format!("📋 گزارش حضور و غیاب {school_name}\n"));
    full.push_str(&format!("📅 تاریخ: {jalali_full}\n"));

    if is_whole_school {
        sms.push_str(&format!("گزارش {school_name} - {jalali_short}\n"));
    } else {
        let c = &classes[0];
        let cls_title = format!("{} - {} شعبه {}", c.major, c.grade, to_persian_digits(&c.section.to_string()));
        full.push_str(&format!("🏫 کلاس: {cls_title}\n"));
        sms.push_str(&format!("گزارش {} {} {} - {jalali_short}\n", c.major, c.grade, to_persian_digits(&c.section.to_string())));
    }

    let mut total_full_day = 0i32;
    let mut total_partial = 0i32;
    let mut total_late = 0i32;
    let mut any_class_had_data = false;

    for cls in &classes {
        let snap = db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?;
        let active_periods: Vec<usize> = (0..4)
            .filter(|&p| snap.students.iter().any(|s| s.period_statuses[p] != AttendanceStatus::Unmarked))
            .collect();

        if active_periods.is_empty() {
            continue;
        }
        any_class_had_data = true;

        let mut full_day_ids: HashSet<i64> = HashSet::new();
        let mut full_day_names: Vec<String> = Vec::new();

        if active_periods.len() >= 2 {
            for s in &snap.students {
                let all_absent_or_excused = active_periods.iter().all(|&p| {
                    matches!(s.period_statuses[p], AttendanceStatus::Absent | AttendanceStatus::Excused)
                });
                if all_absent_or_excused {
                    full_day_ids.insert(s.student_id);
                    let all_excused = active_periods.iter().all(|&p| s.period_statuses[p] == AttendanceStatus::Excused);
                    let display = if all_excused {
                        format!("{} {} (موجه)", s.first_name, s.last_name)
                    } else {
                        format!("{} {}", s.first_name, s.last_name)
                    };
                    full_day_names.push(display);
                }
            }
        }

        let mut per_period_entries: Vec<(usize, Vec<String>, Vec<String>)> = Vec::new();
        let mut class_has_any_issue = !full_day_names.is_empty();

        for &p in &active_periods {
            let mut full_items = Vec::new();
            let mut sms_items = Vec::new();
            for s in &snap.students {
                if full_day_ids.contains(&s.student_id) {
                    continue;
                }
                match s.period_statuses[p] {
                    AttendanceStatus::Absent => {
                        total_partial += 1;
                        class_has_any_issue = true;
                        full_items.push(format!("{} {} (غایب)", s.first_name, s.last_name));
                        sms_items.push(format!("{} {}", s.first_name, s.last_name));
                    }
                    AttendanceStatus::Excused => {
                        total_partial += 1;
                        class_has_any_issue = true;
                        full_items.push(format!("{} {} (موجه)", s.first_name, s.last_name));
                        sms_items.push(format!("{} {}(موجه)", s.first_name, s.last_name));
                    }
                    AttendanceStatus::Late => {
                        total_late += 1;
                        class_has_any_issue = true;
                        full_items.push(format!("{} {} (تأخیر)", s.first_name, s.last_name));
                        sms_items.push(format!("{} {}(تأخیر)", s.first_name, s.last_name));
                    }
                    _ => {}
                }
            }
            per_period_entries.push((p, full_items, sms_items));
        }

        total_full_day += full_day_names.len() as i32;

        if is_whole_school {
            if !class_has_any_issue {
                continue;
            }
            let cls_header = format!("{} {} {}", cls.major, cls.grade, to_persian_digits(&cls.section.to_string()));
            full.push_str(&format!("\n────────────\n🏫 {cls_header}\n"));
            sms.push_str(&format!("\n[{cls_header}]\n"));
        } else {
            full.push_str("────────────────────\n");
        }

        if !class_has_any_issue {
            full.push_str("✅ همه دانش‌آموزان در زنگ‌های ثبت‌شده حاضر بودند.\n");
            sms.push_str("همه دانش‌آموزان حاضر بودند.\n");
            continue;
        }

        if !full_day_names.is_empty() {
            let cnt = to_persian_digits(&full_day_names.len().to_string());
            full.push_str(&format!("🔴 غایبین کل روز ({cnt} نفر):\n"));
            for name in &full_day_names {
                full.push_str(&format!("• {name}\n"));
            }
            sms.push_str(&format!("کل روز: {}\n", full_day_names.join("، ")));
        }

        for (p, full_items, sms_items) in per_period_entries {
            if full_items.is_empty() {
                if !is_whole_school {
                    full.push_str(&format!("\n🔔 {}:\n• بدون غیبت/تأخیر جدید\n", PERIOD_NAMES_FULL[p]));
                }
            } else {
                full.push_str(&format!("\n🔔 {}:\n", PERIOD_NAMES_FULL[p]));
                for item in &full_items {
                    full.push_str(&format!("• {item}\n"));
                }
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

pub fn export_daily_xlsx(
    conn: &Connection,
    major: &str,
    grade: &str,
    section: i32,
    date_iso: &str,
    all_classes: bool,
) -> Result<Vec<u8>, CoreError> {
    let classes: Vec<ClassGroup> = if all_classes {
        db::get_classes(conn)?
    } else {
        db::get_classes(conn)?
            .into_iter()
            .filter(|c| c.major == major && c.grade == grade && c.section == section)
            .collect()
    };

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
        let snap = db::get_class_attendance(conn, &cls.major, &cls.grade, cls.section, date_iso, Period::First, "")?;
        let sheet = workbook.add_worksheet();
        let sheet_name = unique_sheet_name(&format!("{} {} {}", cls.major, cls.grade, cls.section), &mut used_names);
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

pub fn export_monthly_xlsx(
    report: &MonthlyClassReport,
    major: &str,
    grade: &str,
    section: i32,
) -> Result<Vec<u8>, CoreError> {
    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();
    let mut used = HashSet::new();
    let name = unique_sheet_name(&format!("ماهانه {}", report.month_label), &mut used);
    sheet.set_name(&name).map_err(|e| CoreError::Import(e.to_string()))?;
    sheet.set_right_to_left(true);

    let header_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0x0D47A1)).set_font_color(Color::White).set_align(FormatAlign::Center);
    let cell_fmt = Format::new().set_font_name("Vazirmatn").set_align(FormatAlign::Center);
    let warn_fmt = Format::new().set_bold().set_font_name("Vazirmatn").set_background_color(Color::RGB(0xFFDADF)).set_font_color(Color::RGB(0xB71C1C)).set_align(FormatAlign::Center);

    let headers = ["ردیف", "رشته و کلاس", "نام", "نام خانوادگی", "نام پدر", "کد ملی", "شماره موبایل", "زنگ حاضر", "زنگ غایب", "غیبت کل روز", "تأخیر", "موجه", "درصد حضور"];
    for (col, h) in headers.iter().enumerate() {
        let _ = sheet.write_string_with_format(0, col as u16, *h, &header_fmt);
    }

    let cls_label = format!("{major} - {grade} شعبه {section}");
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

pub fn export_monthly_csv(
    report: &MonthlyClassReport,
    major: &str,
    grade: &str,
    section: i32,
) -> String {
    let mut csv = String::with_capacity(report.students.len() * 120 + 256);
    csv.push('\u{FEFF}');
    csv.push_str("ردیف,ماه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل,زنگ حاضر,زنگ غایب,غیبت کل روز,تأخیر,موجه,درصد حضور\n");
    for (idx, s) in report.students.iter().enumerate() {
        csv.push_str(&format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.1}%\n",
            idx + 1, report.month_label, major, grade, section,
            s.first_name, s.last_name, s.father_name, s.national_id, s.mobile,
            s.present_periods, s.absent_periods, s.full_absent_days,
            s.late_periods, s.excused_periods, s.attendance_percent
        ));
    }
    csv
}

fn unique_sheet_name(raw: &str, used: &mut HashSet<String>) -> String {
    let sanitized: String = raw.chars().filter(|c| !matches!(c, ':' | '\\' | '/' | '?' | '*' | '[' | ']')).collect();
    let mut base: String = sanitized.chars().take(28).collect();
    if base.trim().is_empty() {
        base = "Sheet".into();
    }
    if used.insert(base.clone()) {
        return base;
    }
    for n in 2..99 {
        let candidate = format!("{}_{}", base.chars().take(25).collect::<String>(), n);
        if used.insert(candidate.clone()) {
            return candidate;
        }
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
    AttendanceStatus, ClassAttendanceSnapshot, ClassGroup, CoreError, ImportReport,
    JalaliYearMonth, MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary,
    PrincipalReportBundle, StudentAttendanceRow,
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

    pub fn import_file_bytes(
        &self,
        file_name: String,
        bytes: Vec<u8>,
        replace_existing: bool,
    ) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        importer::import_file_bytes(&mut conn, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_classes(&conn)
    }

    pub fn get_class_attendance(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        period: Period,
        search_query: String,
    ) -> Result<ClassAttendanceSnapshot, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_class_attendance(&conn, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(
        &self,
        student_id: i64,
        date_iso: String,
        period: Period,
        status: AttendanceStatus,
        note: String,
    ) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_attendance(&conn, student_id, &date_iso, period, status, &note)
    }

    pub fn mark_class_status(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        period: Period,
        status: AttendanceStatus,
        only_unmarked: bool,
    ) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::mark_class_status(&conn, &major, &grade, section, &date_iso, period, status, only_unmarked)
    }

    pub fn copy_from_previous_period(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        target_period: Period,
    ) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::copy_from_previous_period(&conn, &major, &grade, section, &date_iso, target_period)
    }

    pub fn export_daily_csv(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
    ) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::export_daily_csv(&conn, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        whole_school: bool,
    ) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::export_daily_xlsx(&conn, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn generate_principal_report(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        whole_school: bool,
    ) -> Result<PrincipalReportBundle, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        if whole_school {
            reports::generate_principal_report(&conn, None, None, None, &date_iso)
        } else {
            reports::generate_principal_report(&conn, Some(&major), Some(&grade), Some(section), &date_iso)
        }
    }

    pub fn get_monthly_report(
        &self,
        major: String,
        grade: String,
        section: i32,
        jalali_year: i32,
        jalali_month: i32,
    ) -> Result<MonthlyClassReport, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(
        &self,
        major: String,
        grade: String,
        section: i32,
        jalali_year: i32,
        jalali_month: i32,
    ) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&report, &major, &grade, section)
    }

    pub fn export_monthly_csv(
        &self,
        major: String,
        grade: String,
        section: i32,
        jalali_year: i32,
        jalali_month: i32,
    ) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&report, &major, &grade, section))
    }

    pub fn format_jalali_date(&self, date_iso: String) -> String {
        persian::format_iso_to_jalali(&date_iso)
    }

    pub fn get_jalali_year_month(&self, date_iso: String) -> JalaliYearMonth {
        let (y, m) = persian::iso_to_jalali_year_month(&date_iso);
        JalaliYearMonth {
            year: y,
            month: m as i32,
            label: persian::format_jalali_month_label(y, m),
        }
    }

    pub fn save_principal_phone(&self, phone: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_setting(&conn, "principal_phone", &persian::normalize_mobile(&phone))
    }

    pub fn get_principal_phone(&self) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_setting(&conn, "principal_phone")
    }

    pub fn student_count(&self) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        conn.query_row("SELECT COUNT(*) FROM students", [], |r| r.get(0))
            .map_err(|e| CoreError::Database(e.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE_CSV: &str = "\
ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544
6,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,آیدین,دست پاک,محمد,4700154942,9179478103
11,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,علی,رئیسیان,حسن,4700155019,9179943041
133,هنرستان شهید آوینی,الکتروتکنیک,دوازدهم,1,بنیامین,طاهری,فرشاد,441746977,9124409109
";

    #[test]
    fn test_full_flow_avini_school() {
        let engine = AttendanceEngine::new(":memory:".into()).unwrap();
        let rep = engine.import_file_bytes("avini.csv".into(), SAMPLE_CSV.as_bytes().to_vec(), true).unwrap();
        assert_eq!(rep.imported_count, 4);
        assert_eq!(rep.classes_count, 2);

        let elec = engine.get_class_attendance("الکتروتکنیک".into(), "دوازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(elec.students[0].national_id, "0441746977");
        assert_eq!(elec.students[0].mobile, "09124409109");

        let chem = engine.get_class_attendance("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        let azadi = chem.students[0].student_id;
        let dastpak = chem.students[1].student_id;
        let raisian = chem.students[2].student_id;

        for p in [Period::First, Period::Second, Period::Third, Period::Fourth] {
            engine.set_attendance(azadi, "2025-10-12".into(), p, AttendanceStatus::Absent, "".into()).unwrap();
            engine.set_attendance(dastpak, "2025-10-12".into(), p, if p == Period::First { AttendanceStatus::Absent } else { AttendanceStatus::Present }, "".into()).unwrap();
            engine.set_attendance(raisian, "2025-10-12".into(), p, if p == Period::Second { AttendanceStatus::Late } else { AttendanceStatus::Present }, "".into()).unwrap();
        }

        let pr = engine.generate_principal_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), false).unwrap();
        assert_eq!(pr.full_text.matches("محمد آزادی").count(), 1);
        assert_eq!(pr.sms_text.matches("محمد آزادی").count(), 1);

        let xlsx = engine.export_daily_xlsx("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), true).unwrap();
        assert!(xlsx.starts_with(b"PK\x03\x04"));

        let monthly = engine.get_monthly_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, 1404, 7).unwrap();
        assert_eq!(monthly.month_label, "مهر ۱۴۰۴");
        assert_eq!(monthly.students[0].full_absent_days, 1);
    }
}
''',

    # ===================== ANDROID APP =====================
    "android-app/settings.gradle.kts": r'''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "HozoorApp"
include(":app")
''',

    "android-app/build.gradle.kts": r'''plugins {
    id("com.android.application") version "8.9.1" apply false
    id("org.jetbrains.kotlin.android") version "2.1.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.20" apply false
}
''',

    "android-app/gradle.properties": r'''org.gradle.jvmargs=-Xmx3072m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
''',

    "android-app/app/proguard-rules.pro": r'''-keep class com.sun.jna.** { *; }
-keep class * implements com.sun.jna.** { *; }
-keep class uniffi.hozoor_core.** { *; }
-dontwarn java.awt.**
-dontwarn com.sun.jna.**
''',

    "android-app/app/build.gradle.kts": r'''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "ir.hozoor.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "ir.hozoor.app"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.1.0"
    }

    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "release.jks")
            storePassword = System.getenv("KEYSTORE_PASS") ?: "hozoor123456"
            keyAlias = System.getenv("KEY_ALIAS") ?: "hozoor"
            keyPassword = System.getenv("KEY_PASS") ?: "hozoor123456"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a")
            isUniversalApk = true
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.05.00")
    implementation(composeBom)

    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.compose.material3:material3:1.4.0-alpha15")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.compose.ui:ui")

    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")

    implementation("net.java.dev.jna:jna:5.15.0@aar")
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
}
''',

    "android-app/app/src/main/AndroidManifest.xml": r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:name=".HozoorApplication"
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher_hozoor"
        android:label="حضور"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
''',

    "android-app/app/src/main/res/xml/file_paths.xml": r'''<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="exports" path="exports/" />
</paths>
''',

    "android-app/app/src/main/res/drawable/ic_launcher_hozoor.xml": r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#1B8A5A"
        android:pathData="M24,8 L84,8 C93,8 100,15 100,24 L100,84 C100,93 93,100 84,100 L24,100 C15,100 8,93 8,84 L8,24 C8,15 15,8 24,8 Z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M45,72 L27,54 L34,47 L45,58 L74,29 L81,36 Z" />
</vector>
''',

    "android-app/app/src/main/assets/sample_avini.csv": r'''ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544
2,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,مهدی,بهروزی,بهرام,5150303194,9172893258
3,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,عرفان,حمیرانی,عادل,4700154462,9179551801
4,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,عبدالله,خیاری,یوسف,4700146761,9059553110
5,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,محمد,دریاپیما,عبدالحکیم,3560361826,9173956721
27,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,2,ابراهیم,احمدی,راشد,3560366232,9179739834
55,هنرستان شهید آوینی,الکتروتکنیک,دهم,1,امیرعلی,آریان فر,محمد,4700157801,9173629540
133,هنرستان شهید آوینی,الکتروتکنیک,دوازدهم,1,بنیامین,طاهری,فرشاد,441746977,9124409109
144,هنرستان شهید آوینی,ساختمان,یازدهم,1,امیرحسین,ابراهیمی,محمد,4700154403,9173643201
190,هنرستان شهید آوینی,ساختمان,دوازدهم,1,ابراهیم,رکابکار,عبدالملک,4700139617,9173642185
''',

    "android-app/app/src/main/java/ir/hozoor/app/HozoorApplication.kt": r'''package ir.hozoor.app

import android.app.Application
import uniffi.hozoor_core.AttendanceEngine
import java.io.File

class HozoorApplication : Application() {
    lateinit var engine: AttendanceEngine
        private set

    override fun onCreate() {
        super.onCreate()
        val dbFile = File(filesDir, "hozoor_attendance.db")
        engine = AttendanceEngine(dbFile.absolutePath)
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/MainActivity.kt": r'''package ir.hozoor.app

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.remember
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import ir.hozoor.app.ui.screens.AttendanceScreen
import ir.hozoor.app.ui.state.AttendanceViewModel
import ir.hozoor.app.ui.theme.HozoorExpressiveTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = application as HozoorApplication

        setContent {
            val reduceMotion = remember {
                val am = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
                val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
                am.isLowRamDevice || pm.isPowerSaveMode || Build.VERSION.SDK_INT < Build.VERSION_CODES.P
            }

            HozoorExpressiveTheme(reduceMotion = reduceMotion) {
                val vm: AttendanceViewModel = viewModel(
                    factory = object : ViewModelProvider.Factory {
                        @Suppress("UNCHECKED_CAST")
                        override fun <T : ViewModel> create(modelClass: Class<T>): T {
                            return AttendanceViewModel(app.engine) as T
                        }
                    }
                )
                AttendanceScreen(viewModel = vm)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/util/FileShareHelper.kt": r'''package ir.hozoor.app.util

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import java.io.File

object FileShareHelper {
    fun shareBytesAsFile(
        context: Context,
        fileName: String,
        mimeType: String,
        bytes: ByteArray,
        chooserTitle: String
    ) {
        val dir = File(context.cacheDir, "exports").apply { mkdirs() }
        val file = File(dir, fileName)
        file.writeBytes(bytes)
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)

        val intent = Intent(Intent.ACTION_SEND).apply {
            type = mimeType
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_SUBJECT, fileName)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, chooserTitle))
    }

    fun openSmsApp(context: Context, phone: String, body: String) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = Uri.parse("smsto:${phone.trim()}")
            putExtra("sms_body", body)
        }
        context.startActivity(intent)
    }

    fun shareText(context: Context, text: String, title: String) {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
        }
        context.startActivity(Intent.createChooser(intent, title))
    }

    fun copyToClipboard(context: Context, label: String, text: String) {
        val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText(label, text))
    }

    fun resolveFileName(context: Context, uri: Uri): String {
        context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx >= 0 && cursor.moveToFirst()) {
                return cursor.getString(idx) ?: "students.xlsx"
            }
        }
        return "students.xlsx"
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/theme/Type.kt": r'''package ir.hozoor.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import ir.hozoor.app.R

val VazirmatnFontFamily = FontFamily(
    Font(R.font.vazirmatn_regular, FontWeight.Normal),
    Font(R.font.vazirmatn_medium, FontWeight.Medium),
    Font(R.font.vazirmatn_bold, FontWeight.Bold),
    Font(R.font.vazirmatn_extrabold, FontWeight.ExtraBold),
)

private val Base = Typography()

val HozoorTypography = Typography(
    displayLarge = Base.displayLarge.copy(fontFamily = VazirmatnFontFamily),
    displayMedium = Base.displayMedium.copy(fontFamily = VazirmatnFontFamily),
    displaySmall = Base.displaySmall.copy(fontFamily = VazirmatnFontFamily),
    headlineLarge = Base.headlineLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.ExtraBold),
    headlineMedium = Base.headlineMedium.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    headlineSmall = Base.headlineSmall.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleLarge = Base.titleLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleMedium = Base.titleMedium.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleSmall = Base.titleSmall.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Medium),
    bodyLarge = Base.bodyLarge.copy(fontFamily = VazirmatnFontFamily),
    bodyMedium = Base.bodyMedium.copy(fontFamily = VazirmatnFontFamily),
    bodySmall = Base.bodySmall.copy(fontFamily = VazirmatnFontFamily),
    labelLarge = Base.labelLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Medium),
    labelMedium = Base.labelMedium.copy(fontFamily = VazirmatnFontFamily),
    labelSmall = Base.labelSmall.copy(fontFamily = VazirmatnFontFamily),
)
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/theme/Theme.kt": r'''package ir.hozoor.app.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.MaterialExpressiveTheme
import androidx.compose.material3.MotionScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.expressiveLightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection

object StatusColors {
    val Present = Color(0xFF1B8A5A)
    val PresentContainer = Color(0xFFD7F5E6)
    val Absent = Color(0xFFD93848)
    val AbsentContainer = Color(0xFFFFDADF)
    val Late = Color(0xFFC87A00)
    val LateContainer = Color(0xFFFFECC7)
    val Excused = Color(0xFF3367D6)
    val ExcusedContainer = Color(0xFFDCE7FF)
    val Unmarked = Color(0xFF757982)
}

private val ExpressiveDarkFallback = darkColorScheme(
    primary = Color(0xFF8CD3FF),
    onPrimary = Color(0xFF00344C),
    primaryContainer = Color(0xFF004C6D),
    secondary = Color(0xFFB5CCDD),
    tertiary = Color(0xFFD9BDFE),
    background = Color(0xFF101418),
    surface = Color(0xFF101418),
    surfaceContainerHigh = Color(0xFF1E252B)
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun HozoorExpressiveTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    reduceMotion: Boolean = false,
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> ExpressiveDarkFallback
        else -> expressiveLightColorScheme()
    }
    val motionScheme = if (reduceMotion) MotionScheme.standard() else MotionScheme.expressive()

    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        MaterialExpressiveTheme(
            colorScheme = colorScheme,
            motionScheme = motionScheme,
            typography = HozoorTypography,
            content = content
        )
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/state/AttendanceViewModel.kt": r'''package ir.hozoor.app.ui.state

import androidx.compose.runtime.Immutable
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import uniffi.hozoor_core.AttendanceEngine
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.ClassGroup
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.PrincipalReportBundle
import uniffi.hozoor_core.StudentAttendanceRow
import java.time.LocalDate

@Immutable
data class AttendanceUiState(
    val isLoading: Boolean = true,
    val activeTab: Int = 0,
    val schoolName: String = "هنرستان شهید آوینی",
    val classes: List<ClassGroup> = emptyList(),
    val selectedClass: ClassGroup? = null,
    val selectedDate: LocalDate = LocalDate.now(),
    val jalaliDate: String = "",
    val selectedPeriod: Period = Period.FIRST,
    val searchQuery: String = "",
    val students: List<StudentAttendanceRow> = emptyList(),
    val summary: PeriodSummary = PeriodSummary(0, 0, 0, 0, 0, 0),
    val principalPhone: String = "",
    val principalReport: PrincipalReportBundle? = null,
    val reportWholeSchool: Boolean = false,
    val monthlyYear: Int = 1404,
    val monthlyMonth: Int = 7,
    val monthlyReport: MonthlyClassReport? = null,
    val sortMonthlyByAbsence: Boolean = false,
    val snackbarMessage: String? = null
)

class AttendanceViewModel(private val engine: AttendanceEngine) : ViewModel() {

    private val _uiState = MutableStateFlow(AttendanceUiState())
    val uiState: StateFlow<AttendanceUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val savedPhone = withContext(Dispatchers.IO) { engine.getPrincipalPhone() }
            val ym = engine.getJalaliYearMonth(LocalDate.now().toString())
            _uiState.update {
                it.copy(
                    principalPhone = savedPhone,
                    monthlyYear = ym.year,
                    monthlyMonth = ym.month
                )
            }
            refreshClassesAndData()
        }
    }

    fun switchTab(tabIndex: Int) {
        _uiState.update { it.copy(activeTab = tabIndex) }
        if (tabIndex == 1) loadMonthlyReport()
    }

    fun refreshClassesAndData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val classes = withContext(Dispatchers.IO) { engine.getClasses() }
            val currentSelected = _uiState.value.selectedClass
            val activeClass = classes.find {
                it.major == currentSelected?.major &&
                    it.grade == currentSelected?.grade &&
                    it.section == currentSelected?.section
            } ?: classes.firstOrNull()

            _uiState.update {
                it.copy(
                    classes = classes,
                    selectedClass = activeClass,
                    schoolName = activeClass?.schoolName ?: it.schoolName,
                    jalaliDate = engine.formatJalaliDate(it.selectedDate.toString())
                )
            }
            loadAttendanceSnapshot()
            if (_uiState.value.activeTab == 1) loadMonthlyReport()
        }
    }

    fun selectPeriod(period: Period) {
        if (_uiState.value.selectedPeriod == period) return
        _uiState.update { it.copy(selectedPeriod = period) }
        loadAttendanceSnapshot()
    }

    fun selectClass(group: ClassGroup) {
        _uiState.update { it.copy(selectedClass = group, schoolName = group.schoolName) }
        loadAttendanceSnapshot()
        if (_uiState.value.activeTab == 1) loadMonthlyReport()
    }

    fun shiftDate(days: Long) {
        _uiState.update { it.copy(selectedDate = it.selectedDate.plusDays(days)) }
        loadAttendanceSnapshot()
    }

    fun shiftJalaliMonth(delta: Int) {
        val cur = _uiState.value
        var y = cur.monthlyYear
        var m = cur.monthlyMonth + delta
        if (m > 12) { m = 1; y += 1 }
        if (m < 1) { m = 12; y -= 1 }
        _uiState.update { it.copy(monthlyYear = y, monthlyMonth = m) }
        loadMonthlyReport()
    }

    fun toggleMonthlySort() {
        _uiState.update { it.copy(sortMonthlyByAbsence = !it.sortMonthlyByAbsence) }
    }

    fun updateSearch(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
        loadAttendanceSnapshot()
    }

    fun setStudentStatus(studentId: Long, status: AttendanceStatus) {
        val state = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setAttendance(studentId, state.selectedDate.toString(), state.selectedPeriod, status, "")
            }
            loadAttendanceSnapshot()
        }
    }

    fun markRemainingPresent() {
        val state = _uiState.value
        val group = state.selectedClass ?: return
        viewModelScope.launch {
            val count = withContext(Dispatchers.IO) {
                engine.markClassStatus(
                    group.major, group.grade, group.section,
                    state.selectedDate.toString(), state.selectedPeriod,
                    AttendanceStatus.PRESENT, true
                )
            }
            loadAttendanceSnapshot()
            showMessage("وضعیت حاضر برای $count دانش‌آموز ثبت شد")
        }
    }

    fun copyFromPreviousPeriod() {
        val state = _uiState.value
        val group = state.selectedClass ?: return
        if (state.selectedPeriod == Period.FIRST) {
            showMessage("زنگ اول، زنگ قبلی ندارد")
            return
        }
        viewModelScope.launch {
            val copied = withContext(Dispatchers.IO) {
                engine.copyFromPreviousPeriod(
                    group.major, group.grade, group.section,
                    state.selectedDate.toString(), state.selectedPeriod
                )
            }
            loadAttendanceSnapshot()
            showMessage(if (copied > 0) "وضعیت $copied نفر از زنگ قبل کپی شد" else "در زنگ قبل موردی ثبت نشده است")
        }
    }

    fun importFileBytes(fileName: String, bytes: ByteArray, replaceExisting: Boolean = false) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val report = withContext(Dispatchers.IO) {
                    engine.importFileBytes(fileName, bytes, replaceExisting)
                }
                refreshClassesAndData()
                showMessage("${report.importedCount} دانش‌آموز در ${report.classesCount} کلاس وارد شد")
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
                showMessage("خطا در خواندن فایل: ${e.message}")
            }
        }
    }

    fun preparePrincipalReport(wholeSchool: Boolean = _uiState.value.reportWholeSchool) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        _uiState.update { it.copy(reportWholeSchool = wholeSchool) }
        viewModelScope.launch {
            val bundle = withContext(Dispatchers.IO) {
                engine.generatePrincipalReport(cls.major, cls.grade, cls.section, state.selectedDate.toString(), wholeSchool)
            }
            _uiState.update { it.copy(principalReport = bundle) }
        }
    }

    fun updatePrincipalPhone(phone: String) {
        _uiState.update { it.copy(principalPhone = phone) }
        viewModelScope.launch(Dispatchers.IO) { engine.savePrincipalPhone(phone) }
    }

    fun exportDailyExcel(wholeSchool: Boolean, onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) {
                engine.exportDailyXlsx(cls.major, cls.grade, cls.section, state.selectedDate.toString(), wholeSchool)
            }
            val prefix = if (wholeSchool) "hozoor_school" else "hozoor_${cls.major}_${cls.grade}_${cls.section}"
            onReady("${prefix}_${state.selectedDate}.xlsx", bytes)
        }
    }

    fun exportCurrentClassCsv(onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) {
                engine.exportDailyCsv(cls.major, cls.grade, cls.section, state.selectedDate.toString())
            }
            onReady("hozoor_${cls.major}_${cls.grade}_${cls.section}_${state.selectedDate}.csv", csv.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportMonthlyExcel(onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) {
                engine.exportMonthlyXlsx(cls.major, cls.grade, cls.section, state.monthlyYear, state.monthlyMonth)
            }
            onReady("monthly_${cls.major}_${cls.grade}_${cls.section}_${state.monthlyYear}_${state.monthlyMonth}.xlsx", bytes)
        }
    }

    fun exportMonthlyCsv(onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) {
                engine.exportMonthlyCsv(cls.major, cls.grade, cls.section, state.monthlyYear, state.monthlyMonth)
            }
            onReady(
                "monthly_${cls.major}_${cls.grade}_${cls.section}_${state.monthlyYear}_${state.monthlyMonth}.csv",
                csv.toByteArray(Charsets.UTF_8)
            )
        }
    }

    fun showMessage(msg: String) {
        _uiState.update { it.copy(snackbarMessage = msg) }
    }

    fun clearSnackbar() {
        _uiState.update { it.copy(snackbarMessage = null) }
    }

    private fun loadMonthlyReport() {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val report = withContext(Dispatchers.IO) {
                engine.getMonthlyReport(cls.major, cls.grade, cls.section, state.monthlyYear, state.monthlyMonth)
            }
            _uiState.update { it.copy(monthlyReport = report) }
        }
    }

    private fun loadAttendanceSnapshot() {
        val state = _uiState.value
        val group = state.selectedClass
        if (group == null) {
            _uiState.update {
                it.copy(
                    isLoading = false,
                    students = emptyList(),
                    summary = PeriodSummary(0, 0, 0, 0, 0, 0),
                    jalaliDate = engine.formatJalaliDate(state.selectedDate.toString())
                )
            }
            return
        }
        viewModelScope.launch {
            val snap = withContext(Dispatchers.IO) {
                engine.getClassAttendance(
                    group.major, group.grade, group.section,
                    state.selectedDate.toString(), state.selectedPeriod, state.searchQuery
                )
            }
            _uiState.update {
                it.copy(
                    isLoading = false,
                    jalaliDate = snap.jalaliDate,
                    summary = snap.summary,
                    students = snap.students
                )
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/PeriodSelector.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.NotificationsActive
import androidx.compose.material3.ButtonGroupDefaults
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.ToggleButton
import androidx.compose.material3.ToggleButtonDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import uniffi.hozoor_core.Period

private val ALL_PERIODS = listOf(
    Period.FIRST to "زنگ ۱",
    Period.SECOND to "زنگ ۲",
    Period.THIRD to "زنگ ۳",
    Period.FOURTH to "زنگ ۴"
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun PeriodSelector(
    selectedPeriod: Period,
    onSelectPeriod: (Period) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(ButtonGroupDefaults.ConnectedSpaceBetween)
    ) {
        ALL_PERIODS.forEachIndexed { index, (period, label) ->
            val checked = selectedPeriod == period
            val shapes = when (index) {
                0 -> ButtonGroupDefaults.connectedLeadingButtonShapes()
                ALL_PERIODS.lastIndex -> ButtonGroupDefaults.connectedTrailingButtonShapes()
                else -> ButtonGroupDefaults.connectedMiddleButtonShapes()
            }

            ToggleButton(
                checked = checked,
                onCheckedChange = {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onSelectPeriod(period)
                },
                modifier = Modifier.weight(1f),
                shapes = shapes,
                colors = ToggleButtonDefaults.toggleButtonColors(
                    checkedContainerColor = MaterialTheme.colorScheme.primary,
                    checkedContentColor = MaterialTheme.colorScheme.onPrimary,
                    containerColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                    contentColor = MaterialTheme.colorScheme.onSurfaceVariant
                )
            ) {
                if (checked) {
                    Icon(Icons.Rounded.NotificationsActive, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                }
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = if (checked) FontWeight.Bold else FontWeight.Medium,
                    maxLines = 1
                )
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/StudentAttendanceCard.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Call
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.VerifiedUser
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.StudentAttendanceRow

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    onStatusChange: (AttendanceStatus) -> Unit,
    onSendSms: (StudentAttendanceRow) -> Unit,
    onCallParent: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val cardCorner by animateDpAsState(
        targetValue = if (student.currentStatus == AttendanceStatus.UNMARKED) 18.dp else 28.dp,
        animationSpec = MaterialTheme.motionScheme.fastSpatialSpec(),
        label = "cardCorner"
    )

    val containerTint = when (student.currentStatus) {
        AttendanceStatus.PRESENT -> StatusColors.PresentContainer.copy(alpha = 0.45f)
        AttendanceStatus.ABSENT -> StatusColors.AbsentContainer.copy(alpha = 0.55f)
        AttendanceStatus.LATE -> StatusColors.LateContainer.copy(alpha = 0.50f)
        AttendanceStatus.EXCUSED -> StatusColors.ExcusedContainer.copy(alpha = 0.50f)
        AttendanceStatus.UNMARKED -> MaterialTheme.colorScheme.surfaceContainerLow
    }

    Surface(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 5.dp),
        shape = RoundedCornerShape(cardCorner),
        color = containerTint,
        tonalElevation = 1.dp
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(14.dp))
                        .background(statusPrimaryColor(student.currentStatus).copy(alpha = 0.16f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = toPersianDigits(indexInClass.toString()),
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold,
                        color = statusPrimaryColor(student.currentStatus)
                    )
                }

                Spacer(Modifier.width(12.dp))

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "${student.firstName} ${student.lastName}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "فرزند ${student.fatherName}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    student.periodStatuses.forEachIndexed { i, st ->
                        Box(
                            modifier = Modifier
                                .size(22.dp)
                                .clip(CircleShape)
                                .background(statusPrimaryColor(st).copy(alpha = 0.22f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = toPersianDigits((i + 1).toString()),
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = statusPrimaryColor(st)
                            )
                        }
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                StatusActionChip("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onStatusChange(AttendanceStatus.PRESENT)
                }
                StatusActionChip("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onStatusChange(AttendanceStatus.ABSENT)
                }
                StatusActionChip("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onStatusChange(AttendanceStatus.LATE)
                }
                StatusActionChip("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, Modifier.weight(1f)) {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onStatusChange(AttendanceStatus.EXCUSED)
                }
            }

            AnimatedVisibility(
                visible = (student.currentStatus == AttendanceStatus.ABSENT ||
                    student.currentStatus == AttendanceStatus.LATE) && student.mobile.isNotBlank()
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 10.dp),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = toPersianDigits(student.mobile),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.weight(1f)
                    )
                    FilledTonalIconButton(onClick = { onCallParent(student.mobile) }) {
                        Icon(Icons.Rounded.Call, contentDescription = "تماس با ولی")
                    }
                    Spacer(Modifier.width(6.dp))
                    FilledTonalIconButton(onClick = { onSendSms(student) }) {
                        Icon(Icons.Rounded.Sms, contentDescription = "ارسال پیامک به ولی")
                    }
                }
            }
        }
    }
}

@Composable
private fun StatusActionChip(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    activeColor: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg = if (selected) activeColor else MaterialTheme.colorScheme.surface.copy(alpha = 0.85f)
    val fg = if (selected) Color.White else MaterialTheme.colorScheme.onSurfaceVariant
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(if (selected) 50 else 14))
            .background(bg)
            .clickable(onClick = onClick)
            .padding(vertical = 8.dp, horizontal = 4.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(15.dp))
        Spacer(Modifier.width(3.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
            color = fg,
            maxLines = 1
        )
    }
}

fun statusPrimaryColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.PRESENT -> StatusColors.Present
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    AttendanceStatus.UNMARKED -> StatusColors.Unmarked
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) {
        for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c)
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExpressiveToolbar.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.DoneAll
import androidx.compose.material.icons.rounded.Share
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FloatingToolbarDefaults
import androidx.compose.material3.HorizontalFloatingToolbar
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import uniffi.hozoor_core.Period

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun ExpressiveAttendanceToolbar(
    selectedPeriod: Period,
    onMarkRemainingPresent: () -> Unit,
    onCopyFromPrevious: () -> Unit,
    onOpenExportSheet: () -> Unit,
    onImportFile: () -> Unit,
    modifier: Modifier = Modifier
) {
    HorizontalFloatingToolbar(
        expanded = true,
        modifier = modifier,
        colors = FloatingToolbarDefaults.vibrantFloatingToolbarColors(),
        floatingActionButton = {
            FloatingToolbarDefaults.VibrantFloatingActionButton(onClick = onImportFile) {
                Icon(Icons.Rounded.UploadFile, contentDescription = "ورود اکسل یا CSV")
            }
        }
    ) {
        IconButton(onClick = onMarkRemainingPresent) {
            Icon(Icons.Rounded.DoneAll, contentDescription = "حاضر کردن بقیه")
        }
        IconButton(onClick = onCopyFromPrevious, enabled = selectedPeriod != Period.FIRST) {
            Icon(Icons.Rounded.ContentCopy, contentDescription = "کپی از زنگ قبل")
        }
        IconButton(onClick = onOpenExportSheet) {
            Icon(Icons.Rounded.Share, contentDescription = "گزارش مدیر و خروجی")
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExportAndReportSheet.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Phone
import androidx.compose.material.icons.rounded.Send
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import uniffi.hozoor_core.PrincipalReportBundle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportAndReportSheet(
    report: PrincipalReportBundle?,
    wholeSchool: Boolean,
    principalPhone: String,
    onToggleWholeSchool: (Boolean) -> Unit,
    onPrincipalPhoneChange: (String) -> Unit,
    onSendSms: (phone: String, smsText: String) -> Unit,
    onShareText: (String) -> Unit,
    onCopyText: (String) -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onDismiss: () -> Unit
) {
    var previewSmsMode by remember { mutableStateOf(false) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text("گزارش مدیر و خروجی فایل", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
            Spacer(Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = !wholeSchool, onClick = { onToggleWholeSchool(false) }, label = { Text("کلاس فعلی") })
                FilterChip(selected = wholeSchool, onClick = { onToggleWholeSchool(true) }, label = { Text("کل مدرسه") })
                Spacer(Modifier.weight(1f))
                FilterChip(
                    selected = previewSmsMode,
                    onClick = { previewSmsMode = !previewSmsMode },
                    label = { Text(if (previewSmsMode) "متن پیامک" else "متن پیام‌رسان") }
                )
            }

            Spacer(Modifier.height(10.dp))

            val previewText = when {
                report == null -> "در حال آماده‌سازی گزارش..."
                previewSmsMode -> report.smsText
                else -> report.fullText
            }

            Surface(
                shape = RoundedCornerShape(20.dp),
                color = MaterialTheme.colorScheme.surfaceContainerHigh,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(previewText, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(14.dp))
            }

            Spacer(Modifier.height(12.dp))

            OutlinedTextField(
                value = principalPhone,
                onValueChange = onPrincipalPhoneChange,
                label = { Text("شماره موبایل مدیر (برای ارسال پیامک عادی)") },
                placeholder = { Text("0917xxxxxxx") },
                leadingIcon = { Icon(Icons.Rounded.Phone, contentDescription = null) },
                singleLine = true,
                shape = RoundedCornerShape(18.dp),
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(Modifier.height(12.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = { report?.let { onSendSms(principalPhone, it.smsText) } },
                    enabled = report != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Rounded.Sms, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("پیامک عادی")
                }
                FilledTonalButton(
                    onClick = { report?.let { onShareText(it.fullText) } },
                    enabled = report != null,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Rounded.Send, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("ارسال متن")
                }
                OutlinedButton(onClick = { onCopyText(previewText) }, enabled = report != null) {
                    Icon(Icons.Rounded.ContentCopy, contentDescription = "کپی")
                }
            }

            Spacer(Modifier.height(14.dp))
            Text("خروجی فایل روزانه", style = MaterialTheme.typography.titleSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Spacer(Modifier.height(8.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.TableChart, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("فایل اکسل (.xlsx)")
                }
                OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Description, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text("فایل CSV")
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/MonthlyReportScreen.kt": r'''package ir.hozoor.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Sort
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.MonthlyStudentStat
import java.util.Locale

@Composable
fun MonthlyReportContent(
    report: MonthlyClassReport?,
    sortByAbsence: Boolean,
    onShiftMonth: (Int) -> Unit,
    onToggleSort: () -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    modifier: Modifier = Modifier
) {
    val students = remember(report, sortByAbsence) {
        val list = report?.students.orEmpty()
        if (sortByAbsence) list.sortedByDescending { it.absentPeriods } else list
    }

    Column(modifier = modifier.fillMaxSize()) {
        Surface(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
            shape = RoundedCornerShape(24.dp),
            color = MaterialTheme.colorScheme.surfaceContainerHigh
        ) {
            Column(modifier = Modifier.padding(14.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    IconButton(onClick = { onShiftMonth(-1) }) {
                        Icon(Icons.Rounded.ChevronRight, contentDescription = "ماه قبل")
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(report?.monthLabel ?: "—", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                        Text(
                            text = "روزهای ثبت‌شده: ${toPersianDigits((report?.recordedDays ?: 0).toString())} روز",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = { onShiftMonth(1) }) {
                        Icon(Icons.Rounded.ChevronLeft, contentDescription = "ماه بعد")
                    }
                }

                Spacer(Modifier.height(10.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                    MonthlyKpi("میانگین حضور", "${toPersianDigits(String.format(Locale.US, "%.1f", report?.averageAttendancePercent ?: 100.0))}٪", StatusColors.Present)
                    MonthlyKpi("غیبت کل روز", toPersianDigits((report?.totalFullAbsentDays ?: 0).toString()), StatusColors.Absent)
                    MonthlyKpi("مجموع زنگ غیبت", toPersianDigits((report?.totalAbsentPeriods ?: 0).toString()), StatusColors.Late)
                }

                Spacer(Modifier.height(12.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                        Icon(Icons.Rounded.TableChart, contentDescription = null)
                        Spacer(Modifier.width(4.dp))
                        Text("اکسل ماهانه")
                    }
                    OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                        Icon(Icons.Rounded.Description, contentDescription = null)
                        Spacer(Modifier.width(4.dp))
                        Text("CSV ماهانه")
                    }
                    FilterChip(selected = sortByAbsence, onClick = onToggleSort, label = { Icon(Icons.Rounded.Sort, contentDescription = "مرتب‌سازی") })
                }
            }
        }

        LazyColumn(modifier = Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 28.dp, top = 4.dp)) {
            itemsIndexed(items = students, key = { _, s -> s.studentId }) { idx, stat ->
                MonthlyStudentCard(index = idx + 1, stat = stat)
            }
        }
    }
}

@Composable
private fun MonthlyKpi(title: String, value: String, color: androidx.compose.ui.graphics.Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(title, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun MonthlyStudentCard(index: Int, stat: MonthlyStudentStat) {
    val pct = (stat.attendancePercent / 100.0).toFloat().coerceIn(0f, 1f)
    val barColor = when {
        stat.attendancePercent >= 90.0 -> StatusColors.Present
        stat.attendancePercent >= 75.0 -> StatusColors.Late
        else -> StatusColors.Absent
    }
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 5.dp),
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "${toPersianDigits(index.toString())}. ${stat.firstName} ${stat.lastName}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                Text(
                    text = "${toPersianDigits(String.format(Locale.US, "%.1f", stat.attendancePercent))}٪",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.ExtraBold,
                    color = barColor
                )
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(progress = { pct }, color = barColor, modifier = Modifier.fillMaxWidth().height(6.dp))
            Spacer(Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("حاضر: ${toPersianDigits(stat.presentPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Present)
                Text("غایب: ${toPersianDigits(stat.absentPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Absent)
                Text("کل روز: ${toPersianDigits(stat.fullAbsentDays.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Absent)
                Text("تأخیر: ${toPersianDigits(stat.latePeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Late)
                Text("موجه: ${toPersianDigits(stat.excusedPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Excused)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/AttendanceScreen.kt": r'''package ir.hozoor.app.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.LoadingIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ir.hozoor.app.ui.components.ExportAndReportSheet
import ir.hozoor.app.ui.components.ExpressiveAttendanceToolbar
import ir.hozoor.app.ui.components.PeriodSelector
import ir.hozoor.app.ui.components.StudentAttendanceCard
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.state.AttendanceViewModel
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.util.FileShareHelper
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary

private val IMPORT_MIME_TYPES = arrayOf(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/csv",
    "text/comma-separated-values",
    "application/csv",
    "text/plain"
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class, ExperimentalMaterial3Api::class)
@Composable
fun AttendanceScreen(viewModel: AttendanceViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    var showExportSheet by remember { mutableStateOf(false) }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri ?: return@rememberLauncherForActivityResult
        val name = FileShareHelper.resolveFileName(context, uri)
        context.contentResolver.openInputStream(uri)?.use { stream ->
            viewModel.importFileBytes(fileName = name, bytes = stream.readBytes(), replaceExisting = false)
        }
    }

    LaunchedEffect(state.snackbarMessage) {
        state.snackbarMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            Column(modifier = Modifier.fillMaxSize()) {
                // هدر مدرسه و تاریخ شمسی
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(state.schoolName, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold)
                        Text(state.jalaliDate, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                    }
                    if (state.activeTab == 0) {
                        IconButton(onClick = { viewModel.shiftDate(-1) }) {
                            Icon(Icons.Rounded.ChevronRight, contentDescription = "روز قبل")
                        }
                        IconButton(onClick = { viewModel.shiftDate(1) }) {
                            Icon(Icons.Rounded.ChevronLeft, contentDescription = "روز بعد")
                        }
                    }
                }

                // تب‌های روزانه و ماهانه
                if (state.classes.isNotEmpty()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        FilterChip(
                            selected = state.activeTab == 0,
                            onClick = { viewModel.switchTab(0) },
                            label = { Text("حضور و غیاب روزانه") },
                            modifier = Modifier.weight(1f)
                        )
                        FilterChip(
                            selected = state.activeTab == 1,
                            onClick = { viewModel.switchTab(1) },
                            label = { Text("گزارش ماهانه") },
                            modifier = Modifier.weight(1f)
                        )
                    }

                    // لیست کلاس‌ها
                    LazyRow(
                        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 4.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(items = state.classes, key = { "${it.major}_${it.grade}_${it.section}" }) { cls ->
                            FilterChip(
                                selected = cls == state.selectedClass,
                                onClick = { viewModel.selectClass(cls) },
                                label = {
                                    Text("${cls.major} • ${cls.grade} ${toPersianDigits(cls.section.toString())} (${toPersianDigits(cls.studentCount.toString())})")
                                }
                            )
                        }
                    }
                }

                when {
                    state.isLoading -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            LoadingIndicator()
                        }
                    }
                    state.classes.isEmpty() -> {
                        EmptyImportState(
                            onImportClick = { filePicker.launch(IMPORT_MIME_TYPES) },
                            onLoadSampleClick = {
                                runCatching {
                                    context.assets.open("sample_avini.csv").use { s ->
                                        viewModel.importFileBytes("sample_avini.csv", s.readBytes(), true)
                                    }
                                }
                            }
                        )
                    }
                    state.activeTab == 1 -> {
                        MonthlyReportContent(
                            report = state.monthlyReport,
                            sortByAbsence = state.sortMonthlyByAbsence,
                            onShiftMonth = viewModel::shiftJalaliMonth,
                            onToggleSort = viewModel::toggleMonthlySort,
                            onExportExcel = {
                                viewModel.exportMonthlyExcel { name, bytes ->
                                    FileShareHelper.shareBytesAsFile(
                                        context, name,
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        bytes, "خروجی اکسل ماهانه"
                                    )
                                }
                            },
                            onExportCsv = {
                                viewModel.exportMonthlyCsv { name, bytes ->
                                    FileShareHelper.shareBytesAsFile(context, name, "text/csv", bytes, "خروجی CSV ماهانه")
                                }
                            }
                        )
                    }
                    else -> {
                        Spacer(Modifier.height(4.dp))
                        PeriodSelector(selectedPeriod = state.selectedPeriod, onSelectPeriod = viewModel::selectPeriod)
                        SummaryHeaderCard(summary = state.summary)
                        OutlinedTextField(
                            value = state.searchQuery,
                            onValueChange = viewModel::updateSearch,
                            placeholder = { Text("جستجوی نام، نام خانوادگی یا کد ملی...") },
                            leadingIcon = { Icon(Icons.Rounded.Search, contentDescription = null) },
                            singleLine = true,
                            shape = RoundedCornerShape(24.dp),
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                        )

                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(bottom = 96.dp, top = 4.dp)
                        ) {
                            itemsIndexed(items = state.students, key = { _, s -> s.studentId }, contentType = { _, _ -> "student" }) { idx, student ->
                                StudentAttendanceCard(
                                    indexInClass = idx + 1,
                                    student = student,
                                    onStatusChange = { viewModel.setStudentStatus(student.studentId, it) },
                                    onCallParent = { phone ->
                                        context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone")))
                                    },
                                    onSendSms = { s ->
                                        val pTitle = when (state.selectedPeriod) {
                                            Period.FIRST -> "زنگ اول"
                                            Period.SECOND -> "زنگ دوم"
                                            Period.THIRD -> "زنگ سوم"
                                            Period.FOURTH -> "زنگ چهارم"
                                        }
                                        val body = "با سلام، ولی محترم دانش‌آموز ${s.firstName} ${s.lastName}؛ " +
                                            "ایشان در تاریخ ${state.jalaliDate} ($pTitle) در ${state.schoolName} غایب/دارای تأخیر بوده‌اند."
                                        FileShareHelper.openSmsApp(context, s.mobile, body)
                                    }
                                )
                            }
                        }
                    }
                }
            }

            if (state.activeTab == 0 && state.classes.isNotEmpty()) {
                ExpressiveAttendanceToolbar(
                    selectedPeriod = state.selectedPeriod,
                    onMarkRemainingPresent = viewModel::markRemainingPresent,
                    onCopyFromPrevious = viewModel::copyFromPreviousPeriod,
                    onOpenExportSheet = {
                        viewModel.preparePrincipalReport(false)
                        showExportSheet = true
                    },
                    onImportFile = { filePicker.launch(IMPORT_MIME_TYPES) },
                    modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp)
                )
            }
        }
    }

    if (showExportSheet) {
        ExportAndReportSheet(
            report = state.principalReport,
            wholeSchool = state.reportWholeSchool,
            principalPhone = state.principalPhone,
            onToggleWholeSchool = { viewModel.preparePrincipalReport(it) },
            onPrincipalPhoneChange = viewModel::updatePrincipalPhone,
            onSendSms = { phone, sms -> FileShareHelper.openSmsApp(context, phone, sms) },
            onShareText = { txt -> FileShareHelper.shareText(context, txt, "ارسال گزارش به مدیر") },
            onCopyText = { txt ->
                FileShareHelper.copyToClipboard(context, "گزارش مدیر", txt)
                viewModel.showMessage("متن گزارش کپی شد")
                showExportSheet = false
            },
            onExportExcel = {
                viewModel.exportDailyExcel(state.reportWholeSchool) { name, bytes ->
                    FileShareHelper.shareBytesAsFile(
                        context, name,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        bytes, "خروجی اکسل حضور و غیاب"
                    )
                }
            },
            onExportCsv = {
                viewModel.exportCurrentClassCsv { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "text/csv", bytes, "خروجی CSV حضور و غیاب")
                }
            },
            onDismiss = { showExportSheet = false }
        )
    }
}

@Composable
private fun SummaryHeaderCard(summary: PeriodSummary) {
    val marked = summary.total - summary.unmarked
    val progress = if (summary.total > 0) marked.toFloat() / summary.total else 0f
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainer
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                MetricPill("حاضر", summary.present, StatusColors.Present)
                MetricPill("غایب", summary.absent, StatusColors.Absent)
                MetricPill("تأخیر", summary.late, StatusColors.Late)
                MetricPill("موجه", summary.excused, StatusColors.Excused)
                MetricPill("باقیمانده", summary.unmarked, StatusColors.Unmarked)
            }
            Spacer(Modifier.height(8.dp))
            LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth().height(6.dp))
        }
    }
}

@Composable
private fun MetricPill(label: String, count: Int, color: androidx.compose.ui.graphics.Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(toPersianDigits(count.toString()), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun EmptyImportState(onImportClick: () -> Unit, onLoadSampleClick: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("لیست دانش‌آموزان خالی است", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(8.dp))
        Text(
            text = "فایل اکسل (.xlsx) یا CSV مدرسه را انتخاب کنید تا در چند میلی‌ثانیه کلاس‌بندی شود.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(20.dp))
        Button(onClick = onImportClick) {
            Icon(Icons.Rounded.UploadFile, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("انتخاب فایل اکسل یا CSV")
        }
        Spacer(Modifier.height(10.dp))
        FilledTonalButton(onClick = onLoadSampleClick) {
            Text("تست سریع با نمونه هنرستان شهید آوینی")
        }
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
    print(f"\nDone! Generated {len(FILES)} files successfully.")


if __name__ == "__main__":
    main()
