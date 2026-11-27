use thiserror::Error;

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
