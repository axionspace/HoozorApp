use crate::models::{CoreError, ImportReport};
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
