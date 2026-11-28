use crate::db;
use crate::models::{AttendanceStatus, ClassGroup, CoreError, MonthlyClassReport, Period, PrincipalReportBundle};
use crate::persian::{format_iso_to_jalali, format_iso_to_jalali_short, to_persian_digits};
use rusqlite::Connection;
use rust_xlsxwriter::{Color, Format, FormatAlign, Workbook};
use std::collections::{HashMap, HashSet};

const P_FULL: [&str; 4] = ["زنگ اول", "زنگ دوم", "زنگ سوم", "زنگ چهارم"];
const P_SMS: [&str; 4] = ["زنگ ۱", "زنگ ۲", "زنگ ۳", "زنگ ۴"];

/// اگر کلاس در رشته و پایه خودش فقط ۱ شعبه داشته باشد، عبارت «شعبه» حذف می‌شود
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
    for c in all {
        sets.entry((c.major.clone(), c.grade.clone())).or_default().insert(c.section);
    }
    sets.into_iter().map(|(k, v)| (k, v.len() > 1)).collect()
}

fn late_suffix(time: &str, note: &str) -> String {
    let t = to_persian_digits(time);
    match (t.is_empty(), note.trim().is_empty()) {
        (true, true) => "تأخیر".into(),
        (false, true) => format!("تأخیر ساعت {t}"),
        (true, false) => format!("تأخیر - {}", note.trim()),
        (false, false) => format!("تأخیر ساعت {t} - {}", note.trim()),
    }
}

fn exit_suffix(time: &str, note: &str) -> String {
    let t = to_persian_digits(time);
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
