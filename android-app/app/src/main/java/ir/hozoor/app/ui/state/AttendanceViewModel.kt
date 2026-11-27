package ir.hozoor.app.ui.state

import androidx.compose.runtime.Immutable
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import uniffi.hozoor_core.AttendanceEngine
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.BackupStats
import uniffi.hozoor_core.ClassAnalytics
import uniffi.hozoor_core.ClassGroup
import uniffi.hozoor_core.GradeCategory
import uniffi.hozoor_core.JalaliMonthGrid
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.PrincipalReportBundle
import uniffi.hozoor_core.SavedContact
import uniffi.hozoor_core.StudentAttendanceRow
import uniffi.hozoor_core.StudentGradeRow
import java.time.LocalDate

@Immutable
data class AttendanceUiState(
    val isLoading: Boolean = true,
    val activeTab: Int = 0, // 0=حضور روزانه، 1=دفتر نمره، 2=آمار و ماهانه
    val themeMode: String = "system",
    val dynamicColorEnabled: Boolean = true,
    val classes: List<ClassGroup> = emptyList(),
    val majors: List<String> = emptyList(),
    val selectedMajor: String = "",
    val gradesForSelection: List<String> = emptyList(),
    val selectedGrade: String = "",
    val sectionsForSelection: List<Int> = emptyList(),
    val selectedSection: Int = 1,
    val selectedClass: ClassGroup? = null,
    val selectedDate: LocalDate = LocalDate.now(),
    val jalaliDate: String = "",
    val selectedPeriod: Period = Period.FIRST,
    val classTime: String = "08:00",
    val teacherName: String = "",
    val lessonName: String = "",
    val principalPhone: String = "",
    val recipientName: String = "",
    val searchQuery: String = "",
    val isPeriodSaved: Boolean = false,
    val students: List<StudentAttendanceRow> = emptyList(),
    val summary: PeriodSummary = PeriodSummary(0, 0, 0, 0, 0, 0),
    // دفتر نمره مستمر / پودمانی / دلخواه
    val gradeCategories: List<GradeCategory> = emptyList(),
    val selectedGradeCategoryId: Long = 0L,
    val classGrades: List<StudentGradeRow> = emptyList(),
    // مخاطبین و گزارش و پشتیبان
    val savedContacts: List<SavedContact> = emptyList(),
    val classAnalytics: ClassAnalytics? = null,
    val backupStats: BackupStats? = null,
    val principalReport: PrincipalReportBundle? = null,
    val reportWholeSchool: Boolean = false,
    val sheetFeedback: String? = null,
    val monthlyYear: Int = 1404,
    val monthlyMonth: Int = 7,
    val monthlyReport: MonthlyClassReport? = null,
    val sortMonthlyByAbsence: Boolean = false,
    val snackbarMessage: String? = null
)

class AttendanceViewModel(private val engine: AttendanceEngine) : ViewModel() {

    private val _uiState = MutableStateFlow(AttendanceUiState())
    val uiState: StateFlow<AttendanceUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val initData = withContext(Dispatchers.IO) {
                val map = mapOf(
                    "teacher" to engine.getSetting("teacher_name"),
                    "lesson" to engine.getSetting("lesson_name"),
                    "phone" to engine.getSetting("principal_phone"),
                    "theme" to engine.getSetting("theme_mode").ifBlank { "system" },
                    "dynamic" to engine.getSetting("dynamic_color").ifBlank { "true" }
                )
                Triple(map, engine.getGradeCategories(), engine.getSavedContacts())
            }
            val (s, cats, contacts) = initData
            val ym = engine.getJalaliYearMonth(LocalDate.now().toString())
            _uiState.update {
                it.copy(
                    teacherName = s["teacher"].orEmpty(),
                    lessonName = s["lesson"].orEmpty(),
                    principalPhone = s["phone"].orEmpty(),
                    themeMode = s["theme"] ?: "system",
                    dynamicColorEnabled = s["dynamic"] != "false",
                    gradeCategories = cats,
                    selectedGradeCategoryId = cats.firstOrNull()?.id ?: 0L,
                    savedContacts = contacts,
                    monthlyYear = ym.year,
                    monthlyMonth = ym.month
                )
            }
            refreshClassesAndData()
        }
    }

    fun toggleDarkMode(currentlyDark: Boolean) {
        val next = if (currentlyDark) "light" else "dark"
        _uiState.update { it.copy(themeMode = next) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("theme_mode", next) }
    }

    fun toggleDynamicColor() {
        val next = !_uiState.value.dynamicColorEnabled
        _uiState.update { it.copy(dynamicColorEnabled = next) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("dynamic_color", next.toString()) }
        showMessage(if (next) "رنگ پویا (Dynamic Color) فعال شد" else "تم استاندارد فعال شد")
    }

    fun updateTeacherName(v: String) { _uiState.update { it.copy(teacherName = v) }; viewModelScope.launch(Dispatchers.IO) { engine.setSetting("teacher_name", v) } }
    fun updateLessonName(v: String) { _uiState.update { it.copy(lessonName = v) }; viewModelScope.launch(Dispatchers.IO) { engine.setSetting("lesson_name", v) } }
    fun updatePrincipalPhone(v: String) { _uiState.update { it.copy(principalPhone = v) }; viewModelScope.launch(Dispatchers.IO) { engine.setSetting("principal_phone", v) } }
    fun updateRecipient(name: String, phone: String) {
        _uiState.update { it.copy(recipientName = name, principalPhone = phone) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("principal_phone", phone) }
    }
    fun updateClassTime(v: String) { _uiState.update { it.copy(classTime = v) } }

    fun switchTab(tab: Int) {
        _uiState.update { it.copy(activeTab = tab) }
        if (tab == 1) loadGradebook()
        if (tab == 2) loadAnalyticsAndMonthly()
    }

    fun refreshClassesAndData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val all = withContext(Dispatchers.IO) { engine.getClasses() }
            resolveCategories(all, _uiState.value.selectedMajor, _uiState.value.selectedGrade, _uiState.value.selectedSection)
            loadAttendanceSnapshot()
            if (_uiState.value.activeTab == 1) loadGradebook()
            if (_uiState.value.activeTab == 2) loadAnalyticsAndMonthly()
        }
    }

    fun selectMajor(m: String) { resolveCategories(_uiState.value.classes, m, _uiState.value.selectedGrade, _uiState.value.selectedSection); reloadActiveTab() }
    fun selectGrade(g: String) { resolveCategories(_uiState.value.classes, _uiState.value.selectedMajor, g, _uiState.value.selectedSection); reloadActiveTab() }
    fun selectSection(s: Int) { resolveCategories(_uiState.value.classes, _uiState.value.selectedMajor, _uiState.value.selectedGrade, s); reloadActiveTab() }

    private fun reloadActiveTab() {
        loadAttendanceSnapshot()
        when (_uiState.value.activeTab) { 1 -> loadGradebook(); 2 -> loadAnalyticsAndMonthly() }
    }

    private fun resolveCategories(all: List<ClassGroup>, wm: String, wg: String, ws: Int) {
        if (all.isEmpty()) {
            _uiState.update { it.copy(classes = emptyList(), majors = emptyList(), selectedMajor = "", gradesForSelection = emptyList(), selectedGrade = "", sectionsForSelection = emptyList(), selectedSection = 1, selectedClass = null, jalaliDate = engine.formatJalaliDate(it.selectedDate.toString())) }
            return
        }
        val majors = all.map { it.major }.filter { it.isNotBlank() }.distinct()
        val major = when { majors.isEmpty() -> ""; wm in majors -> wm; else -> majors.first() }
        val inM = if (majors.isEmpty()) all else all.filter { it.major == major }
        val grades = inM.map { it.grade }.distinct()
        val grade = if (wg in grades) wg else grades.first()
        val inG = inM.filter { it.grade == grade }
        val sections = inG.map { it.section }.distinct().sorted()
        val section = if (ws in sections) ws else sections.first()
        _uiState.update { it.copy(classes = all, majors = majors, selectedMajor = major, gradesForSelection = grades, selectedGrade = grade, sectionsForSelection = sections, selectedSection = section, selectedClass = inG.find { c -> c.section == section } ?: inG.firstOrNull()) }
    }

    fun selectPeriod(p: Period) {
        val t = when (p) { Period.FIRST -> "08:00"; Period.SECOND -> "09:00"; Period.THIRD -> "10:00"; Period.FOURTH -> "11:00" }
        _uiState.update { it.copy(selectedPeriod = p, classTime = t) }
        loadAttendanceSnapshot()
    }

    fun selectDateIso(iso: String) { runCatching { LocalDate.parse(iso) }.onSuccess { d -> _uiState.update { it.copy(selectedDate = d) }; loadAttendanceSnapshot() } }
    fun shiftDate(days: Long) { _uiState.update { it.copy(selectedDate = it.selectedDate.plusDays(days)) }; loadAttendanceSnapshot() }
    fun getJalaliCalendarGrid(y: Int, m: Int): JalaliMonthGrid = engine.getJalaliMonthGrid(y, m)
    fun currentDateJalaliYearMonth() = engine.getJalaliYearMonth(_uiState.value.selectedDate.toString())

    fun shiftJalaliMonth(delta: Int) {
        val c = _uiState.value
        var y = c.monthlyYear; var m = c.monthlyMonth + delta
        if (m > 12) { m = 1; y += 1 }; if (m < 1) { m = 12; y -= 1 }
        _uiState.update { it.copy(monthlyYear = y, monthlyMonth = m) }
        loadAnalyticsAndMonthly()
    }

    fun toggleMonthlySort() { _uiState.update { it.copy(sortMonthlyByAbsence = !it.sortMonthlyByAbsence) } }
    fun updateSearch(q: String) { _uiState.update { it.copy(searchQuery = q) }; loadAttendanceSnapshot() }

    fun setStudentStatus(studentId: Long, status: AttendanceStatus, exitTime: String = "", note: String = "") {
        val st = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setAttendance(studentId, st.selectedDate.toString(), st.selectedPeriod, status, exitTime, note, st.teacherName, st.lessonName, st.classTime)
            }
            loadAttendanceSnapshot()
        }
    }

    fun resetAllToPresent() {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val n = withContext(Dispatchers.IO) {
                engine.markClassStatus(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod, AttendanceStatus.PRESENT, false, st.teacherName, st.lessonName, st.classTime)
            }
            loadAttendanceSnapshot()
            showMessage("همه $n دانش‌آموز در حالت حاضر ثبت شدند")
        }
    }

    fun copyFromPreviousPeriod() {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        if (st.selectedPeriod == Period.FIRST) { showMessage("زنگ اول، زنگ قبلی ندارد"); return }
        viewModelScope.launch {
            val n = withContext(Dispatchers.IO) { engine.copyFromPreviousPeriod(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod) }
            loadAttendanceSnapshot()
            showMessage(if (n > 0) "وضعیت $n نفر از زنگ قبل کپی شد" else "در زنگ قبل موردی ثبت نشده است")
        }
    }

    // ===== دفتر نمره =====
    fun selectGradeCategory(catId: Long) { _uiState.update { it.copy(selectedGradeCategoryId = catId) }; loadGradebook() }

    fun addGradeCategory(name: String) {
        viewModelScope.launch {
            try {
                val newId = withContext(Dispatchers.IO) { engine.addGradeCategory(name) }
                val cats = withContext(Dispatchers.IO) { engine.getGradeCategories() }
                _uiState.update { it.copy(gradeCategories = cats, selectedGradeCategoryId = newId) }
                loadGradebook()
                showMessage("عنوان «$name» اضافه شد")
            } catch (e: Exception) { showMessage(e.message ?: "خطا") }
        }
    }

    fun deleteGradeCategory(catId: Long) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { engine.deleteGradeCategory(catId) }
            val cats = withContext(Dispatchers.IO) { engine.getGradeCategories() }
            _uiState.update { it.copy(gradeCategories = cats, selectedGradeCategoryId = cats.firstOrNull()?.id ?: 0L) }
            loadGradebook()
            showMessage("عنوان نمره حذف شد")
        }
    }

    fun setStudentGrade(studentId: Long, categoryId: Long, score: String, note: String) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { engine.setStudentGrade(studentId, categoryId, score, note) }
            loadGradebook()
            loadAttendanceSnapshot()
            showMessage("نمره ثبت شد")
        }
    }

    fun exportGradebookExcel(onReady: (String, ByteArray) -> Unit) {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) { engine.exportGradebookXlsx(cls.major, cls.grade, cls.section) }
            onReady("grades_${cls.grade}_${cls.section}.xlsx", bytes)
        }
    }

    // ===== مخاطبین =====
    fun saveContact(name: String, role: String, phone: String) {
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) { engine.saveContact(name, role, phone) }
                val contacts = withContext(Dispatchers.IO) { engine.getSavedContacts() }
                _uiState.update { it.copy(savedContacts = contacts, recipientName = name, principalPhone = phone, sheetFeedback = null) }
                engine.setSetting("principal_phone", phone)
            } catch (e: Exception) { _uiState.update { it.copy(sheetFeedback = e.message) } }
        }
    }

    fun deleteContact(id: Long) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { engine.deleteContact(id) }
            val contacts = withContext(Dispatchers.IO) { engine.getSavedContacts() }
            _uiState.update { it.copy(savedContacts = contacts) }
        }
    }

    // ===== دانش‌آموزان، ورود/خروج و پشتیبان =====
    fun addStudentToCurrentClass(f: String, l: String, fa: String, nid: String, mob: String) {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) { engine.addStudent(cls.schoolName, cls.major, cls.grade, cls.section, f, l, fa, nid, mob) }
                refreshClassesAndData(); showMessage("دانش‌آموز اضافه شد")
            } catch (e: Exception) { showMessage(e.message ?: "خطا") }
        }
    }

    fun updateStudent(id: Long, f: String, l: String, fa: String, nid: String, mob: String) {
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) { engine.updateStudent(id, f, l, fa, nid, mob) }
                loadAttendanceSnapshot(); showMessage("اطلاعات ذخیره شد")
            } catch (e: Exception) { showMessage(e.message ?: "خطا") }
        }
    }

    fun deleteStudent(id: Long) { viewModelScope.launch { withContext(Dispatchers.IO) { engine.deleteStudent(id) }; refreshClassesAndData(); showMessage("دانش‌آموز حذف شد") } }
    fun deleteCurrentClass() {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            val n = withContext(Dispatchers.IO) { engine.deleteClass(cls.major, cls.grade, cls.section) }
            refreshClassesAndData(); showMessage("کلاس و $n دانش‌آموز حذف شدند")
        }
    }

    fun importFileBytes(name: String, bytes: ByteArray, replace: Boolean) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val rep = withContext(Dispatchers.IO) { engine.importFileBytes(name, bytes, replace) }
                refreshClassesAndData(); showMessage("${rep.importedCount} دانش‌آموز در ${rep.classesCount} کلاس وارد شد")
            } catch (e: Exception) { _uiState.update { it.copy(isLoading = false) }; showMessage("خطا: ${e.message}") }
        }
    }

    fun restoreBackupJson(json: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val rep = withContext(Dispatchers.IO) { engine.restoreBackupJson(json) }
                val cats = withContext(Dispatchers.IO) { engine.getGradeCategories() }
                val contacts = withContext(Dispatchers.IO) { engine.getSavedContacts() }
                _uiState.update { it.copy(gradeCategories = cats, selectedGradeCategoryId = cats.firstOrNull()?.id ?: 0L, savedContacts = contacts) }
                refreshClassesAndData(); showMessage("پشتیبان کامل بازیابی شد (${rep.importedCount} دانش‌آموز)")
            } catch (e: Exception) { _uiState.update { it.copy(isLoading = false) }; showMessage(e.message ?: "پشتیبان نامعتبر است") }
        }
    }

    fun exportBackupJson(onReady: (String, ByteArray) -> Unit) {
        val d = _uiState.value.selectedDate
        viewModelScope.launch {
            val json = withContext(Dispatchers.IO) { engine.exportBackupJson() }
            onReady("hozoor_backup_$d.json", json.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportTemplateExcel(onReady: (String, ByteArray) -> Unit) {
        viewModelScope.launch { onReady("نمونه_ورود_دانش_آموزان.xlsx", withContext(Dispatchers.IO) { engine.exportTemplateXlsx() }) }
    }

    fun prepareExportSheet(wholeSchool: Boolean = _uiState.value.reportWholeSchool) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        _uiState.update { it.copy(reportWholeSchool = wholeSchool, sheetFeedback = null) }
        viewModelScope.launch {
            val (bundle, stats, contacts) = withContext(Dispatchers.IO) {
                Triple(
                    engine.generatePrincipalReport(cls.major, cls.grade, cls.section, st.selectedDate.toString(), wholeSchool, st.teacherName),
                    engine.getBackupStats(),
                    engine.getSavedContacts()
                )
            }
            _uiState.update { it.copy(principalReport = bundle, backupStats = stats, savedContacts = contacts) }
        }
    }

    fun generatePeriodGroupMessage(target: AttendanceStatus, onReady: (String) -> Unit) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        _uiState.update { it.copy(sheetFeedback = null) }
        viewModelScope.launch {
            try {
                val msg = withContext(Dispatchers.IO) {
                    engine.generatePeriodGroupMessage(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod, target, st.teacherName, st.lessonName, st.reportWholeSchool)
                }
                onReady(msg)
            } catch (e: Exception) { _uiState.update { it.copy(sheetFeedback = e.message ?: "موردی یافت نشد") } }
        }
    }

    fun setSheetFeedback(msg: String?) { _uiState.update { it.copy(sheetFeedback = msg) } }

    fun exportDailyExcel(whole: Boolean, onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val b = withContext(Dispatchers.IO) { engine.exportDailyXlsx(cls.major, cls.grade, cls.section, st.selectedDate.toString(), whole) }
            onReady("${if (whole) "hozoor_all" else "hozoor_${cls.grade}_${cls.section}"}_${st.selectedDate}.xlsx", b)
        }
    }

    fun exportCurrentClassCsv(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val c = withContext(Dispatchers.IO) { engine.exportDailyCsv(cls.major, cls.grade, cls.section, st.selectedDate.toString()) }
            onReady("hozoor_${cls.grade}_${cls.section}_${st.selectedDate}.csv", c.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportMonthlyExcel(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val b = withContext(Dispatchers.IO) { engine.exportMonthlyXlsx(cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth) }
            onReady("monthly_${cls.grade}_${cls.section}_${st.monthlyYear}_${st.monthlyMonth}.xlsx", b)
        }
    }

    fun exportMonthlyCsv(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val c = withContext(Dispatchers.IO) { engine.exportMonthlyCsv(cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth) }
            onReady("monthly_${cls.grade}_${cls.section}_${st.monthlyYear}_${st.monthlyMonth}.csv", c.toByteArray(Charsets.UTF_8))
        }
    }

    fun showMessage(msg: String) { _uiState.update { it.copy(snackbarMessage = msg) } }
    fun clearSnackbar() { _uiState.update { it.copy(snackbarMessage = null) } }

    private fun loadGradebook() {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        val catId = st.selectedGradeCategoryId.takeIf { it > 0 } ?: st.gradeCategories.firstOrNull()?.id ?: return
        viewModelScope.launch {
            val rows = withContext(Dispatchers.IO) { engine.getClassGrades(cls.major, cls.grade, cls.section, catId) }
            _uiState.update { it.copy(selectedGradeCategoryId = catId, classGrades = rows) }
        }
    }

    private fun loadAnalyticsAndMonthly() {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val (a, m) = withContext(Dispatchers.IO) {
                engine.getClassAnalytics(cls.major, cls.grade, cls.section) to
                    engine.getMonthlyReport(cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth)
            }
            _uiState.update { it.copy(classAnalytics = a, monthlyReport = m) }
        }
    }

    private fun loadAttendanceSnapshot() {
        val st = _uiState.value; val cls = st.selectedClass
        if (cls == null) {
            _uiState.update { it.copy(isLoading = false, students = emptyList(), isPeriodSaved = false, summary = PeriodSummary(0, 0, 0, 0, 0, 0), jalaliDate = engine.formatJalaliDate(st.selectedDate.toString())) }
            return
        }
        viewModelScope.launch {
            val snap = withContext(Dispatchers.IO) { engine.getClassAttendance(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod, st.searchQuery) }
            _uiState.update { it.copy(isLoading = false, jalaliDate = snap.jalaliDate, isPeriodSaved = snap.isPeriodSaved, summary = snap.summary, students = snap.students) }
        }
    }
}
