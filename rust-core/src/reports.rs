use crate::db;
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
