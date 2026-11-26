mod db;
mod importer;
mod models;
mod persian;
mod reports;

pub use models::{
    AttendanceStatus, ClassAttendanceSnapshot, ClassGroup, CoreError, ImportReport,
    JalaliYearMonth, MonthlyClassReport, MonthlyStudentStat, Period, PeriodSummary,
    PrincipalReportBundle, StudentAttendanceRow,
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

    pub fn import_file_bytes(
        &self,
        file_name: String,
        bytes: Vec<u8>,
        replace_existing: bool,
    ) -> Result<ImportReport, CoreError> {
        let mut conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        importer::import_file_bytes(&mut conn, &file_name, &bytes, replace_existing)
    }

    pub fn get_classes(&self) -> Result<Vec<ClassGroup>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_classes(&conn)
    }

    pub fn get_class_attendance(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        period: Period,
        search_query: String,
    ) -> Result<ClassAttendanceSnapshot, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_class_attendance(&conn, &major, &grade, section, &date_iso, period, &search_query)
    }

    pub fn set_attendance(
        &self,
        student_id: i64,
        date_iso: String,
        period: Period,
        status: AttendanceStatus,
        note: String,
    ) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_attendance(&conn, student_id, &date_iso, period, status, &note)
    }

    pub fn mark_class_status(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        period: Period,
        status: AttendanceStatus,
        only_unmarked: bool,
    ) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::mark_class_status(&conn, &major, &grade, section, &date_iso, period, status, only_unmarked)
    }

    pub fn copy_from_previous_period(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        target_period: Period,
    ) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::copy_from_previous_period(&conn, &major, &grade, section, &date_iso, target_period)
    }

    pub fn export_daily_csv(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
    ) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::export_daily_csv(&conn, &major, &grade, section, &date_iso)
    }

    pub fn export_daily_xlsx(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        whole_school: bool,
    ) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        reports::export_daily_xlsx(&conn, &major, &grade, section, &date_iso, whole_school)
    }

    pub fn generate_principal_report(
        &self,
        major: String,
        grade: String,
        section: i32,
        date_iso: String,
        whole_school: bool,
    ) -> Result<PrincipalReportBundle, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        if whole_school {
            reports::generate_principal_report(&conn, None, None, None, &date_iso)
        } else {
            reports::generate_principal_report(&conn, Some(&major), Some(&grade), Some(section), &date_iso)
        }
    }

    pub fn get_monthly_report(
        &self,
        major: String,
        grade: String,
        section: i32,
        jalali_year: i32,
        jalali_month: i32,
    ) -> Result<MonthlyClassReport, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)
    }

    pub fn export_monthly_xlsx(
        &self,
        major: String,
        grade: String,
        section: i32,
        jalali_year: i32,
        jalali_month: i32,
    ) -> Result<Vec<u8>, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        reports::export_monthly_xlsx(&report, &major, &grade, section)
    }

    pub fn export_monthly_csv(
        &self,
        major: String,
        grade: String,
        section: i32,
        jalali_year: i32,
        jalali_month: i32,
    ) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        let report = db::get_monthly_report(&conn, &major, &grade, section, jalali_year, jalali_month)?;
        Ok(reports::export_monthly_csv(&report, &major, &grade, section))
    }

    pub fn format_jalali_date(&self, date_iso: String) -> String {
        persian::format_iso_to_jalali(&date_iso)
    }

    pub fn get_jalali_year_month(&self, date_iso: String) -> JalaliYearMonth {
        let (y, m) = persian::iso_to_jalali_year_month(&date_iso);
        JalaliYearMonth {
            year: y,
            month: m as i32,
            label: persian::format_jalali_month_label(y, m),
        }
    }

    pub fn save_principal_phone(&self, phone: String) -> Result<(), CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::set_setting(&conn, "principal_phone", &persian::normalize_mobile(&phone))
    }

    pub fn get_principal_phone(&self) -> Result<String, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        db::get_setting(&conn, "principal_phone")
    }

    pub fn student_count(&self) -> Result<i32, CoreError> {
        let conn = self.conn.lock().map_err(|_| CoreError::Database("Lock poisoned".into()))?;
        conn.query_row("SELECT COUNT(*) FROM students", [], |r| r.get(0))
            .map_err(|e| CoreError::Database(e.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE_CSV: &str = "\
ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544
6,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,آیدین,دست پاک,محمد,4700154942,9179478103
11,هنرستان شهید آوینی,صنایع شیمیایی,یازدهم,1,علی,رئیسیان,حسن,4700155019,9179943041
133,هنرستان شهید آوینی,الکتروتکنیک,دوازدهم,1,بنیامین,طاهری,فرشاد,441746977,9124409109
";

    #[test]
    fn test_full_flow_avini_school() {
        let engine = AttendanceEngine::new(":memory:".into()).unwrap();
        let rep = engine.import_file_bytes("avini.csv".into(), SAMPLE_CSV.as_bytes().to_vec(), true).unwrap();
        assert_eq!(rep.imported_count, 4);
        assert_eq!(rep.classes_count, 2);

        let elec = engine.get_class_attendance("الکتروتکنیک".into(), "دوازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        assert_eq!(elec.students[0].national_id, "0441746977");
        assert_eq!(elec.students[0].mobile, "09124409109");

        let chem = engine.get_class_attendance("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), Period::First, "".into()).unwrap();
        let azadi = chem.students[0].student_id;
        let dastpak = chem.students[1].student_id;
        let raisian = chem.students[2].student_id;

        for p in [Period::First, Period::Second, Period::Third, Period::Fourth] {
            engine.set_attendance(azadi, "2025-10-12".into(), p, AttendanceStatus::Absent, "".into()).unwrap();
            engine.set_attendance(dastpak, "2025-10-12".into(), p, if p == Period::First { AttendanceStatus::Absent } else { AttendanceStatus::Present }, "".into()).unwrap();
            engine.set_attendance(raisian, "2025-10-12".into(), p, if p == Period::Second { AttendanceStatus::Late } else { AttendanceStatus::Present }, "".into()).unwrap();
        }

        let pr = engine.generate_principal_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), false).unwrap();
        assert_eq!(pr.full_text.matches("محمد آزادی").count(), 1);
        assert_eq!(pr.sms_text.matches("محمد آزادی").count(), 1);

        let xlsx = engine.export_daily_xlsx("صنایع شیمیایی".into(), "یازدهم".into(), 1, "2025-10-12".into(), true).unwrap();
        assert!(xlsx.starts_with(b"PK\x03\x04"));

        let monthly = engine.get_monthly_report("صنایع شیمیایی".into(), "یازدهم".into(), 1, 1404, 7).unwrap();
        assert_eq!(monthly.month_label, "مهر ۱۴۰۴");
        assert_eq!(monthly.students[0].full_absent_days, 1);
    }
}
