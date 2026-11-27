mod db;
mod importer;
mod models;
mod persian;
mod reports;

pub use models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    ImportReport, JalaliDayCell, JalaliMonthGrid, JalaliYearMonth, MonthlyClassReport,
    MonthlyStudentStat, Period, PeriodSummary, PrincipalReportBundle, StudentAttendanceRow,
    TopStudentCount,
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
        Ok(Arc::new(Self { conn: Mutex::new(db::init_database(&db_path)?) }))
    }

    pub fn import_file_bytes(&self, file_name: String, bytes: Vec<u8>, replace_existing: bool) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        importer::import_file_bytes(&mut conn, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_classes(&conn)
    }

    pub fn get_class_attendance(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, search_query: String) -> Result<ClassAttendanceSnapshot, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_attendance(&conn, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(&self, student_id: i64, date_iso: String, period: Period, status: AttendanceStatus, note: String, teacher_name: String, lesson_name: String, class_time: String) -> Result<(), CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_attendance(&mut conn, student_id, &date_iso, period, status, &note, &teacher_name, &lesson_name, &class_time)
    }

    pub fn set_student_score(&self, student_id: i64, date_iso: String, period: Period, class_score: String, session_score: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_student_score(&conn, student_id, &date_iso, period, &class_score, &session_score)
    }

    pub fn mark_class_status(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher_name: String, lesson_name: String, class_time: String) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::mark_class_status(&conn, &major, &grade, section, &date_iso, period, status, only_unmarked, &teacher_name, &lesson_name, &class_time)
    }

    pub fn copy_from_previous_period(&self, major: String, grade: String, section: i32, date_iso: String, target_period: Period) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::copy_from_previous_period(&conn, &major, &grade, section, &date_iso, target_period)
    }

    pub fn add_student(&self, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String, class_score: String) -> Result<i64, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::add_student(&conn, &school_name, &major, &grade, section, &first_name, &last_name, &father_name, &national_id, &mobile, &class_score)
    }

    pub fn update_student(&self, student_id: i64, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String, class_score: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::update_student(&conn, student_id, &first_name, &last_name, &father_name, &national_id, &mobile, &class_score)
    }

    pub fn delete_student(&self, student_id: i64) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_student(&conn, student_id)
    }

    pub fn delete_class(&self, major: String, grade: String, section: i32) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::delete_class(&conn, &major, &grade, section)
    }

    pub fn get_backup_stats(&self) -> Result<BackupStats, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_backup_stats(&conn)
    }

    pub fn get_class_analytics(&self, major: String, grade: String, section: i32) -> Result<ClassAnalytics, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_class_analytics(&conn, &major, &grade, section)
    }

    pub fn generate_period_group_message(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, target_status: AttendanceStatus, teacher_name: String, lesson_name: String, whole_school: bool) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::generate_period_group_message(&conn, &major, &grade, section, &date_iso, period, target_status, &teacher_name, &lesson_name, whole_school)
    }

    pub fn generate_principal_report(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool, teacher_name: String) -> Result<PrincipalReportBundle, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        if whole_school {
            reports::generate_principal_report(&conn, None, None, None, &date_iso, &teacher_name)
        } else {
            reports::generate_principal_report(&conn, Some(&major), Some(&grade), Some(section), &date_iso, &teacher_name)
        }
    }

    pub fn export_daily_csv(&self, major: String, grade: String, section: i32, date_iso: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_daily_csv(&conn, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        reports::export_daily_xlsx(&conn, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn get_monthly_report(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let rep = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&rep, &major, &grade, section)
    }

    pub fn export_monthly_csv(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let rep = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&rep, &major, &grade, section))
    }

    pub fn export_template_xlsx(&self) -> Result<Vec<u8>, CoreError> { reports::export_template_xlsx() }

    pub fn export_backup_json(&self) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::export_backup_json(&conn)
    }

    pub fn restore_backup_json(&self, json_text: String) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::restore_backup_json(&mut conn, &json_text)
    }

    pub fn format_jalali_date(&self, date_iso: String) -> String { persian::format_iso_to_jalali(&date_iso) }

    pub fn get_jalali_year_month(&self, date_iso: String) -> JalaliYearMonth {
        let (y, m) = persian::iso_to_jalali_year_month(&date_iso);
        JalaliYearMonth { year: y, month: m as i32, label: persian::format_jalali_month_label(y, m) }
    }

    pub fn get_jalali_month_grid(&self, jalali_year: i32, jalali_month: i32) -> JalaliMonthGrid {
        persian::build_jalali_month_grid(jalali_year, jalali_month)
    }

    pub fn set_setting(&self, key: String, value: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_setting(&conn, &key, &value)
    }

    pub fn get_setting(&self, key: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::get_setting(&conn, &key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = "ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل\n\
1,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544\n\
2,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,1,مهدی,بهروزی,بهرام,5150303194,9172893258\n";

    #[test]
    fn test_v3_sms_labels_scores_and_backup() {
        let eng = AttendanceEngine::new(":memory:".into()).unwrap();
        eng.import_file_bytes("s.csv".into(), SAMPLE.as_bytes().to_vec(), true).unwrap();
        let snap = eng.get_class_attendance("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        let (s1, s2) = (snap.students[0].student_id, snap.students[1].student_id);

        eng.set_student_score(s1, "2025-10-12".into(), Period::First, "19.5".into(), "20".into()).unwrap();
        for p in [Period::First, Period::Second, Period::Third, Period::Fourth] {
            eng.set_attendance(s1, "2025-10-12".into(), p, AttendanceStatus::Absent, "".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
            eng.set_attendance(s2, "2025-10-12".into(), p, if p == Period::First { AttendanceStatus::Late } else { AttendanceStatus::Present }, "".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        }
        let pr = eng.generate_principal_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), false, "دبیر".into()).unwrap();
        assert_eq!(pr.sms_text.matches("محمد آزادی").count(), 1);
        assert!(pr.sms_text.contains("(غایب)"));
        assert!(pr.sms_text.contains("(تأخیر)"));
        assert!(pr.sms_text.contains("حاضر"));

        let backup = eng.export_backup_json().unwrap();
        assert!(backup.contains("19.5"));
        let eng2 = AttendanceEngine::new(":memory:".into()).unwrap();
        eng2.restore_backup_json(backup).unwrap();
        assert_eq!(eng2.get_backup_stats().unwrap().scores_count, 2);
    }
}
