mod db;
mod importer;
mod models;
mod persian;
mod reports;

pub use models::{
    AttendanceStatus, BackupStats, ClassAnalytics, ClassAttendanceSnapshot, ClassGroup, CoreError,
    GradeCategory, ImportReport, JalaliDayCell, JalaliMonthGrid, JalaliYearMonth,
    MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary, PrincipalReportBundle,
    SavedContact, StudentAttendanceRow, StudentGradeRow, TopStudentCount,
};

use rusqlite::Connection;
use std::sync::{Arc, Mutex};

uniffi::setup_scaffolding!();

#[derive(uniffi::Object)]
pub struct AttendanceEngine { conn: Mutex<Connection> }

#[uniffi::export]
impl AttendanceEngine {
    #[uniffi::constructor]
    pub fn new(db_path: String) -> Result<Arc<Self>, CoreError> {
        Ok(Arc::new(Self { conn: Mutex::new(db::init_database(&db_path)?) }))
    }

    pub fn import_file_bytes(&self, file_name: String, bytes: Vec<u8>, replace_existing: bool) -> Result<ImportReport, CoreError> {
        let mut c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        importer::import_file_bytes(&mut c, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        db::get_classes(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?)
    }

    pub fn get_class_attendance(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, search_query: String) -> Result<ClassAttendanceSnapshot, CoreError> {
        db::get_class_attendance(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(&self, student_id: i64, date_iso: String, period: Period, status: AttendanceStatus, exit_time: String, note: String, teacher_name: String, lesson_name: String, class_time: String) -> Result<(), CoreError> {
        let mut c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::set_attendance(&mut c, student_id, &date_iso, period, status, &exit_time, &note, &teacher_name, &lesson_name, &class_time)
    }

    pub fn mark_class_status(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, status: AttendanceStatus, only_unmarked: bool, teacher_name: String, lesson_name: String, class_time: String) -> Result<i32, CoreError> {
        db::mark_class_status(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, &date_iso, period, status, only_unmarked, &teacher_name, &lesson_name, &class_time)
    }

    pub fn copy_from_previous_period(&self, major: String, grade: String, section: i32, date_iso: String, target_period: Period) -> Result<i32, CoreError> {
        db::copy_from_previous_period(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, &date_iso, target_period)
    }

    pub fn add_student(&self, school_name: String, major: String, grade: String, section: i32, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<i64, CoreError> {
        db::add_student(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &school_name, &major, &grade, section, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn update_student(&self, student_id: i64, first_name: String, last_name: String, father_name: String, national_id: String, mobile: String) -> Result<(), CoreError> {
        db::update_student(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, student_id, &first_name, &last_name, &father_name, &national_id, &mobile)
    }

    pub fn delete_student(&self, student_id: i64) -> Result<(), CoreError> {
        db::delete_student(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, student_id)
    }

    pub fn delete_class(&self, major: String, grade: String, section: i32) -> Result<i32, CoreError> {
        db::delete_class(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section)
    }

    pub fn get_grade_categories(&self) -> Result<Vec<GradeCategory>, CoreError> {
        db::get_grade_categories(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?)
    }

    pub fn add_grade_category(&self, name: String) -> Result<i64, CoreError> {
        db::add_grade_category(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &name)
    }

    pub fn delete_grade_category(&self, category_id: i64) -> Result<(), CoreError> {
        db::delete_grade_category(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, category_id)
    }

    pub fn get_class_grades(&self, major: String, grade: String, section: i32, category_id: i64) -> Result<Vec<StudentGradeRow>, CoreError> {
        db::get_class_grades(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, category_id)
    }

    pub fn set_student_grade(&self, student_id: i64, category_id: i64, score: String, note: String) -> Result<(), CoreError> {
        db::set_student_grade(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, student_id, category_id, &score, &note)
    }

    pub fn export_gradebook_xlsx(&self, major: String, grade: String, section: i32) -> Result<Vec<u8>, CoreError> {
        reports::export_gradebook_xlsx(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section)
    }

    pub fn get_saved_contacts(&self) -> Result<Vec<SavedContact>, CoreError> {
        db::get_saved_contacts(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?)
    }

    pub fn save_contact(&self, name: String, role: String, phone: String) -> Result<i64, CoreError> {
        db::save_contact(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &name, &role, &phone)
    }

    pub fn delete_contact(&self, contact_id: i64) -> Result<(), CoreError> {
        db::delete_contact(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, contact_id)
    }

    pub fn get_backup_stats(&self) -> Result<BackupStats, CoreError> {
        db::get_backup_stats(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?)
    }

    pub fn get_class_analytics(&self, major: String, grade: String, section: i32) -> Result<ClassAnalytics, CoreError> {
        db::get_class_analytics(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section)
    }

    pub fn generate_period_group_message(&self, major: String, grade: String, section: i32, date_iso: String, period: Period, target_status: AttendanceStatus, teacher_name: String, lesson_name: String, whole_school: bool) -> Result<String, CoreError> {
        reports::generate_period_group_message(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, &date_iso, period, target_status, &teacher_name, &lesson_name, whole_school)
    }

    pub fn generate_principal_report(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool, teacher_name: String) -> Result<PrincipalReportBundle, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        if whole_school { reports::generate_principal_report(&c, None, None, None, &date_iso, &teacher_name) }
        else { reports::generate_principal_report(&c, Some(&major), Some(&grade), Some(section), &date_iso, &teacher_name) }
    }

    pub fn export_daily_csv(&self, major: String, grade: String, section: i32, date_iso: String) -> Result<String, CoreError> {
        reports::export_daily_csv(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(&self, major: String, grade: String, section: i32, date_iso: String, whole_school: bool) -> Result<Vec<u8>, CoreError> {
        reports::export_daily_xlsx(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn get_monthly_report(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<MonthlyClassReport, CoreError> {
        db::get_monthly_report(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<Vec<u8>, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let r = db::get_monthly_report(&c, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&r, &major, &grade, section)
    }

    pub fn export_monthly_csv(&self, major: String, grade: String, section: i32, jalali_year: i32, jalali_month: i32) -> Result<String, CoreError> {
        let c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        let r = db::get_monthly_report(&c, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&r, &major, &grade, section))
    }

    pub fn export_template_xlsx(&self) -> Result<Vec<u8>, CoreError> { reports::export_template_xlsx() }

    pub fn export_backup_json(&self) -> Result<String, CoreError> {
        db::export_backup_json(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?)
    }

    pub fn restore_backup_json(&self, json_text: String) -> Result<ImportReport, CoreError> {
        let mut c = self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?;
        db::restore_backup_json(&mut c, &json_text)
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
        db::set_setting(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &key, &value)
    }

    pub fn get_setting(&self, key: String) -> Result<String, CoreError> {
        db::get_setting(&*self.conn.lock().map_err(|_| CoreError::Database("Lock".into()))?, &key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    const SAMPLE: &str = "ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل\n1,نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544\n";

    #[test]
    fn test_v4_left_class_gradebook_contacts_backup() {
        let e = AttendanceEngine::new(":memory:".into()).unwrap();
        e.import_file_bytes("s.csv".into(), SAMPLE.as_bytes().to_vec(), true).unwrap();
        let snap = e.get_class_attendance("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        let sid = snap.students[0].student_id;

        e.set_attendance(sid, "2025-10-12".into(), Period::First, AttendanceStatus::LeftClass, "09:42".into(), "برنگشت".into(), "دبیر".into(), "شیمی".into(), "08:00".into()).unwrap();
        let rep = e.generate_principal_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), false, "دبیر".into()).unwrap();
        assert!(rep.sms_text.contains("۰۹:۴۲"));

        let cats = e.get_grade_categories().unwrap();
        assert!(cats.len() >= 9);
        let custom_id = e.add_grade_category("مستمر بهمن".into()).unwrap();
        e.set_student_grade(sid, custom_id, "19.5".into(), "عالی".into()).unwrap();
        assert!(e.export_gradebook_xlsx("صنایع شیمیایی".into(), "یازدهم".into(), 1).unwrap().starts_with(b"PK\x03\x04"));

        e.save_contact("آقای رضایی".into(), "مدیر".into(), "09171234567".into()).unwrap();
        let bk = e.export_backup_json().unwrap();
        let e2 = AttendanceEngine::new(":memory:".into()).unwrap();
        e2.restore_backup_json(bk).unwrap();
        let st = e2.get_backup_stats().unwrap();
        assert_eq!(st.grades_count, 1);
        assert_eq!(st.contacts_count, 1);
    }
}
