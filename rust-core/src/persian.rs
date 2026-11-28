use crate::models::{JalaliDayCell, JalaliMonthGrid};

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
