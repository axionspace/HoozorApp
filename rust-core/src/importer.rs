use crate::models::{CoreError, ImportReport};
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
