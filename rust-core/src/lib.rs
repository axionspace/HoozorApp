mod db;
mod importer;
mod models;
mod persian;
mod reports;

pub use models::{
    AttendanceStatus, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError, ImportReport,
    JalaliDayCell, JalaliMonthGrid, JalaliYearMonth, MonthlyClassReport, MonthlyStudentStat,
    Period, PeriodSummary, PrincipalReportBundle, StudentAttendanceRow, TopStudentCount,
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

    pub fn import_file_bytes(&self, file_name: String, bytes: Vec<u8>, replace_existing: bool) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        importer::import_file_bytes(&mut conn, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_classes(&conn)
    }

    pub fn get_class_attendance(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, period: Period, search_query: String) -> Result<ClassAttendanceSnapshot, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_class_attendance(&conn, &school_name, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(&self, student_id: i64, date_iso: String, period: Period, status: AttendanceStatus, note: String, teacher_name: String, lesson_name: String, class_time: String) -> Result<(), CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_attendance(&mut conn, student_id, &date_iso, period, status, &note, &teacher_name, &lesson_name, &class_time)
    }

    pub fn mark_class_status(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher_name: String, lesson_name: String, class_time: String) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::mark_class_status(&conn, &school_name, &major, &grade, section, &date_iso, period, status, only_unmarked, &teacher_name, &lesson_name, &class_time)
    }

    pub fn copy_from_previous_period(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, target_period: Period) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::copy_from_previous_period(&conn, &school_name, &major, &grade, section, &date_iso, target_period)
    }

    pub fn add_student(&self, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<i64, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::add_student(&conn, &school_name, &major, &grade, section, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn update_student(&self, student_id: i64, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::update_student(&conn, student_id, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn delete_student(&self, student_id: i64) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::delete_student(&conn, student_id)
    }

    pub fn delete_class(&self, school_name: String, major: String, grade: String, section: i32) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::delete_class(&conn, &school_name, &major, &grade, section)
    }

    pub fn get_class_analytics(&self, school_name: String, major: String, grade: String, section: i32) -> Result<ClassAnalytics, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_class_analytics(&conn, &school_name, &major, &grade, section)
    }

    pub fn generate_period_group_message(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, period: Period, target_status: AttendanceStatus, teacher_name: String, lesson_name: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::generate_period_group_message(&conn, &school_name, &major, &grade, section, &date_iso, period, target_status, &teacher_name, &lesson_name)
    }

    pub fn generate_principal_report(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, whole_school: bool, teacher_name: String) -> Result<PrincipalReportBundle, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        if whole_school {
            reports::generate_principal_report(&conn, &school_name, None, None, None, &date_iso, &teacher_name)
        } else {
            reports::generate_principal_report(&conn, &school_name, Some(&major), Some(&grade), Some(section), &date_iso, &teacher_name)
        }
    }

    pub fn export_daily_csv(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::export_daily_csv(&conn, &school_name, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(&self, school_name: String, major: String, grade: String, section: i32, date_iso: String, whole_school: bool) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::export_daily_xlsx(&conn, &school_name, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn get_monthly_report(&self, school_name: String, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_monthly_report(&conn, &school_name, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(&self, school_name: String, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &school_name, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&report, &major, &grade, section)
    }

    pub fn export_monthly_csv(&self, school_name: String, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &school_name, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&report, &school_name, &major, &grade, section))
    }

    pub fn export_template_xlsx(&self) -> Result<Vec<u8>, CoreError> {
        reports::export_template_xlsx()
    }

    pub fn export_backup_json(&self) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::export_backup_json(&conn)
    }

    pub fn restore_backup_json(&self, json_text: String) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::restore_backup_json(&mut conn, &json_text)
    }

    pub fn format_jalali_date(&self, date_iso: String) -> String {
        persian::format_iso_to_jalali(&date_iso)
    }

    pub fn get_jalali_year_month(&self, date_iso: String) -> JalaliYearMonth {
        let (y, m) = persian::iso_to_jalali_year_month(&date_iso);
        JalaliYearMonth { year: y, month: m as i32, label: persian::format_jalali_month_label(y, m) }
    }

    pub fn get_jalali_month_grid(&self, jalali_year: i32, jalali_month: i32) -> JalaliMonthGrid {
        persian::build_jalali_month_grid(jalali_year, jalali_month)
    }

    pub fn set_setting(&self, key: String, value: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_setting(&conn, &key, &value)
    }

    pub fn get_setting(&self, key: String) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_setting(&conn, &key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const TEST_CSV: &str = "\
ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,مدرسه نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544
2,مدرسه نمونه,صنایع شیمیایی,یازدهم,1,مهدی,بهروزی,بهرام,5150303194,9172893258
3,دبیرستان متوسطه اول,,هفتم,1,پارسا,رحیمی,جواد,441746977,9124409109
";

    #[test]
    fn test_default_present_reset_all_backup_and_reports() {
        let engine = AttendanceEngine::new(":memory:".into()).unwrap();
        let rep = engine.import_file_bytes("test.csv".into(), TEST_CSV.as_bytes().to_vec(), true).unwrap();
        assert_eq!(rep.imported_count, 3);
        assert_eq!(rep.classes_count, 2);

        let snap = engine.get_class_attendance("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(snap.summary.present, 2);
        assert_eq!(snap.students[0].current_status, AttendanceStatus::Present);

        let s1 = snap.students[0].student_id;
        engine.set_attendance(s1, "2025-10-12".into(), Period::First, AttendanceStatus::Absent, "".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        let snap2 = engine.get_class_attendance("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(snap2.summary.absent, 1);

        engine.mark_class_status("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, AttendanceStatus::Present, false, "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        let snap3 = engine.get_class_attendance("مدرسه نمونه".into(), "صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(snap3.summary.present, 2);
        assert_eq!(snap3.summary.absent, 0);

        let backup = engine.export_backup_json().unwrap();
        let engine2 = AttendanceEngine::new(":memory:".into()).unwrap();
        assert_eq!(engine2.restore_backup_json(backup).unwrap().imported_count, 3);
        assert!(engine.export_template_xlsx().unwrap().starts_with(b"PK\x03\x04"));
        assert_eq!(engine.get_jalali_month_grid(1404, 7).days.len(), 30);
    }
}
