use crate::db;
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
