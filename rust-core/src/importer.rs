use crate::models::{CoreError, ImportReport};
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
