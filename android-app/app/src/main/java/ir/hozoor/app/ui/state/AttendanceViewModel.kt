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
import uniffi.hozoor_core.JalaliMonthGrid
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.PrincipalReportBundle
import uniffi.hozoor_core.StudentAttendanceRow
import java.time.LocalDate

@Immutable
data class AttendanceUiState(
    val isLoading: Boolean = true,
    val activeTab: Int = 0,
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
    val searchQuery: String = "",
    val isPeriodSaved: Boolean = false,
    val students: List<StudentAttendanceRow> = emptyList(),
    val summary: PeriodSummary = PeriodSummary(0, 0, 0, 0, 0, 0),
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
            val s = withContext(Dispatchers.IO) {
                mapOf(
                    "teacher" to engine.getSetting("teacher_name"),
                    "lesson" to engine.getSetting("lesson_name"),
                    "phone" to engine.getSetting("principal_phone"),
                    "theme" to engine.getSetting("theme_mode").ifBlank { "system" },
                    "dynamic" to engine.getSetting("dynamic_color").ifBlank { "true" }
                )
            }
            val ym = engine.getJalaliYearMonth(LocalDate.now().toString())
            _uiState.update {
                it.copy(
                    teacherName = s["teacher"].orEmpty(),
                    lessonName = s["lesson"].orEmpty(),
                    principalPhone = s["phone"].orEmpty(),
                    themeMode = s["theme"] ?: "system",
                    dynamicColorEnabled = s["dynamic"] != "false",
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
        showMessage(if (next) "رنگ پویا (Dynamic Color) فعال شد" else "پالت استاندارد فعال شد")
    }

    fun updateTeacherName(v: String) {
        _uiState.update { it.copy(teacherName = v) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("teacher_name", v) }
    }

    fun updateLessonName(v: String) {
        _uiState.update { it.copy(lessonName = v) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("lesson_name", v) }
    }

    fun updatePrincipalPhone(v: String) {
        _uiState.update { it.copy(principalPhone = v) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("principal_phone", v) }
    }

    fun updateClassTime(v: String) { _uiState.update { it.copy(classTime = v) } }

    fun switchTab(tab: Int) {
        _uiState.update { it.copy(activeTab = tab) }
        if (tab == 1) loadAnalyticsAndMonthly()
    }

    fun refreshClassesAndData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val all = withContext(Dispatchers.IO) { engine.getClasses() }
            resolveCategories(all, _uiState.value.selectedMajor, _uiState.value.selectedGrade, _uiState.value.selectedSection)
            loadAttendanceSnapshot()
            if (_uiState.value.activeTab == 1) loadAnalyticsAndMonthly()
        }
    }

    fun selectMajor(major: String) {
        val st = _uiState.value
        resolveCategories(st.classes, major, st.selectedGrade, st.selectedSection)
        loadAttendanceSnapshot()
        if (st.activeTab == 1) loadAnalyticsAndMonthly()
    }

    fun selectGrade(grade: String) {
        val st = _uiState.value
        resolveCategories(st.classes, st.selectedMajor, grade, st.selectedSection)
        loadAttendanceSnapshot()
        if (st.activeTab == 1) loadAnalyticsAndMonthly()
    }

    fun selectSection(section: Int) {
        val st = _uiState.value
        resolveCategories(st.classes, st.selectedMajor, st.selectedGrade, section)
        loadAttendanceSnapshot()
        if (st.activeTab == 1) loadAnalyticsAndMonthly()
    }

    private fun resolveCategories(all: List<ClassGroup>, wantedMajor: String, wantedGrade: String, wantedSection: Int) {
        if (all.isEmpty()) {
            _uiState.update {
                it.copy(
                    classes = emptyList(), majors = emptyList(), selectedMajor = "",
                    gradesForSelection = emptyList(), selectedGrade = "",
                    sectionsForSelection = emptyList(), selectedSection = 1, selectedClass = null,
                    jalaliDate = engine.formatJalaliDate(it.selectedDate.toString())
                )
            }
            return
        }
        val majors = all.map { it.major }.filter { it.isNotBlank() }.distinct()
        val major = when {
            majors.isEmpty() -> ""
            wantedMajor in majors -> wantedMajor
            else -> majors.first()
        }
        val inMajor = if (majors.isEmpty()) all else all.filter { it.major == major }
        val grades = inMajor.map { it.grade }.distinct()
        val grade = if (wantedGrade in grades) wantedGrade else grades.first()
        val inGrade = inMajor.filter { it.grade == grade }
        val sections = inGrade.map { it.section }.distinct().sorted()
        val section = if (wantedSection in sections) wantedSection else sections.first()
        val cls = inGrade.find { it.section == section } ?: inGrade.firstOrNull()

        _uiState.update {
            it.copy(
                classes = all, majors = majors, selectedMajor = major,
                gradesForSelection = grades, selectedGrade = grade,
                sectionsForSelection = sections, selectedSection = section, selectedClass = cls
            )
        }
    }

    fun selectPeriod(period: Period) {
        val time = when (period) {
            Period.FIRST -> "08:00"
            Period.SECOND -> "09:00"
            Period.THIRD -> "10:00"
            Period.FOURTH -> "11:00"
        }
        _uiState.update { it.copy(selectedPeriod = period, classTime = time) }
        loadAttendanceSnapshot()
    }

    fun selectDateIso(dateIso: String) {
        runCatching { LocalDate.parse(dateIso) }.onSuccess { d ->
            _uiState.update { it.copy(selectedDate = d) }
            loadAttendanceSnapshot()
        }
    }

    fun shiftDate(days: Long) {
        _uiState.update { it.copy(selectedDate = it.selectedDate.plusDays(days)) }
        loadAttendanceSnapshot()
    }

    fun getJalaliCalendarGrid(year: Int, month: Int): JalaliMonthGrid = engine.getJalaliMonthGrid(year, month)
    fun currentDateJalaliYearMonth() = engine.getJalaliYearMonth(_uiState.value.selectedDate.toString())

    fun shiftJalaliMonth(delta: Int) {
        val cur = _uiState.value
        var y = cur.monthlyYear
        var m = cur.monthlyMonth + delta
        if (m > 12) { m = 1; y += 1 }
        if (m < 1) { m = 12; y -= 1 }
        _uiState.update { it.copy(monthlyYear = y, monthlyMonth = m) }
        loadAnalyticsAndMonthly()
    }

    fun toggleMonthlySort() { _uiState.update { it.copy(sortMonthlyByAbsence = !it.sortMonthlyByAbsence) } }
    fun updateSearch(q: String) { _uiState.update { it.copy(searchQuery = q) }; loadAttendanceSnapshot() }

    fun setStudentStatus(studentId: Long, status: AttendanceStatus, targetPeriod: Period = _uiState.value.selectedPeriod) {
        val st = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setAttendance(studentId, st.selectedDate.toString(), targetPeriod, status, "", st.teacherName, st.lessonName, st.classTime)
            }
            loadAttendanceSnapshot()
        }
    }

    /** لمس مستقیم روی عددهای ۱ تا ۴: سبز(حاضر) -> قرمز(غایب) -> زرد(تأخیر) -> آبی(موجه) -> سبز(حاضر) */
    fun cycleStudentPeriodStatus(student: StudentAttendanceRow, periodIndex: Int) {
        val period = when (periodIndex) {
            0 -> Period.FIRST
            1 -> Period.SECOND
            2 -> Period.THIRD
            else -> Period.FOURTH
        }
        val currentRaw = student.periodStatuses.getOrElse(periodIndex) { AttendanceStatus.UNMARKED }
        val next = when (currentRaw) {
            AttendanceStatus.UNMARKED, AttendanceStatus.PRESENT -> AttendanceStatus.ABSENT
            AttendanceStatus.ABSENT -> AttendanceStatus.LATE
            AttendanceStatus.LATE -> AttendanceStatus.EXCUSED
            AttendanceStatus.EXCUSED -> AttendanceStatus.PRESENT
        }
        setStudentStatus(student.studentId, next, period)
    }

    fun saveStudentScore(studentId: Long, classScore: String) {
        val st = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setStudentScore(studentId, st.selectedDate.toString(), st.selectedPeriod, classScore, classScore)
            }
            loadAttendanceSnapshot()
            showMessage("نمره ثبت شد")
        }
    }

    fun resetAllToPresent() {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val count = withContext(Dispatchers.IO) {
                engine.markClassStatus(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod, AttendanceStatus.PRESENT, false, st.teacherName, st.lessonName, st.classTime)
            }
            loadAttendanceSnapshot()
            showMessage("همه $count دانش‌آموز به حالت حاضر برگشتند")
        }
    }

    fun copyFromPreviousPeriod() {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        if (st.selectedPeriod == Period.FIRST) { showMessage("زنگ اول، زنگ قبلی ندارد"); return }
        viewModelScope.launch {
            val copied = withContext(Dispatchers.IO) {
                engine.copyFromPreviousPeriod(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod)
            }
            loadAttendanceSnapshot()
            showMessage(if (copied > 0) "حضور و غیاب $copied نفر از زنگ قبل کپی شد" else "در زنگ قبل موردی ثبت نشده است")
        }
    }

    fun addStudentToCurrentClass(first: String, last: String, father: String, nid: String, mobile: String, score: String) {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) { engine.addStudent(cls.schoolName, cls.major, cls.grade, cls.section, first, last, father, nid, mobile, score) }
                refreshClassesAndData()
                showMessage("دانش‌آموز به کلاس اضافه شد")
            } catch (e: Exception) { showMessage(e.message ?: "خطا در افزودن") }
        }
    }

    fun updateStudent(studentId: Long, first: String, last: String, father: String, nid: String, mobile: String, score: String) {
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) { engine.updateStudent(studentId, first, last, father, nid, mobile, score) }
                loadAttendanceSnapshot()
                showMessage("مشخصات دانش‌آموز ذخیره شد")
            } catch (e: Exception) { showMessage(e.message ?: "خطا در ویرایش") }
        }
    }

    fun deleteStudent(studentId: Long) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { engine.deleteStudent(studentId) }
            refreshClassesAndData()
            showMessage("دانش‌آموز و سوابق او حذف شد")
        }
    }

    fun deleteCurrentClass() {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            val count = withContext(Dispatchers.IO) { engine.deleteClass(cls.major, cls.grade, cls.section) }
            refreshClassesAndData()
            showMessage("کلاس و $count دانش‌آموز حذف شدند")
        }
    }

    fun importFileBytes(fileName: String, bytes: ByteArray, replaceExisting: Boolean) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val rep = withContext(Dispatchers.IO) { engine.importFileBytes(fileName, bytes, replaceExisting) }
                refreshClassesAndData()
                showMessage("${rep.importedCount} دانش‌آموز در ${rep.classesCount} کلاس وارد شد")
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
                showMessage("خطا در خواندن فایل: ${e.message}")
            }
        }
    }

    fun restoreBackupJson(jsonText: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val rep = withContext(Dispatchers.IO) { engine.restoreBackupJson(jsonText) }
                refreshClassesAndData()
                showMessage("پشتیبان کامل بازیابی شد: ${rep.importedCount} دانش‌آموز")
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
                showMessage(e.message ?: "فایل پشتیبان معتبر نیست")
            }
        }
    }

    fun exportBackupJson(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        viewModelScope.launch {
            val json = withContext(Dispatchers.IO) { engine.exportBackupJson() }
            onReady("hozoor_full_backup_${st.selectedDate}.json", json.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportTemplateExcel(onReady: (String, ByteArray) -> Unit) {
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) { engine.exportTemplateXlsx() }
            onReady("نمونه_ورود_دانش_آموزان.xlsx", bytes)
        }
    }

    fun prepareExportSheet(wholeSchool: Boolean = _uiState.value.reportWholeSchool) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        _uiState.update { it.copy(reportWholeSchool = wholeSchool, sheetFeedback = null) }
        viewModelScope.launch {
            val (bundle, stats) = withContext(Dispatchers.IO) {
                engine.generatePrincipalReport(cls.major, cls.grade, cls.section, st.selectedDate.toString(), wholeSchool, st.teacherName) to
                    engine.getBackupStats()
            }
            _uiState.update { it.copy(principalReport = bundle, backupStats = stats) }
        }
    }

    fun generatePeriodGroupMessage(targetStatus: AttendanceStatus, onReady: (String) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        _uiState.update { it.copy(sheetFeedback = null) }
        viewModelScope.launch {
            try {
                val msg = withContext(Dispatchers.IO) {
                    engine.generatePeriodGroupMessage(
                        cls.major, cls.grade, cls.section, st.selectedDate.toString(),
                        st.selectedPeriod, targetStatus, st.teacherName, st.lessonName, st.reportWholeSchool
                    )
                }
                onReady(msg)
            } catch (e: Exception) {
                _uiState.update { it.copy(sheetFeedback = e.message ?: "موردی برای ارسال ثبت نشده است") }
            }
        }
    }

    fun setSheetFeedback(msg: String?) { _uiState.update { it.copy(sheetFeedback = msg) } }

    fun exportDailyExcel(wholeSchool: Boolean, onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) { engine.exportDailyXlsx(cls.major, cls.grade, cls.section, st.selectedDate.toString(), wholeSchool) }
            val pfx = if (wholeSchool) "hozoor_all" else "hozoor_${cls.grade}_${cls.section}"
            onReady("${pfx}_${st.selectedDate}.xlsx", bytes)
        }
    }

    fun exportCurrentClassCsv(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) { engine.exportDailyCsv(cls.major, cls.grade, cls.section, st.selectedDate.toString()) }
            onReady("hozoor_${cls.grade}_${cls.section}_${st.selectedDate}.csv", csv.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportMonthlyExcel(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) { engine.exportMonthlyXlsx(cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth) }
            onReady("monthly_${cls.grade}_${cls.section}_${st.monthlyYear}_${st.monthlyMonth}.xlsx", bytes)
        }
    }

    fun exportMonthlyCsv(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) { engine.exportMonthlyCsv(cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth) }
            onReady("monthly_${cls.grade}_${cls.section}_${st.monthlyYear}_${st.monthlyMonth}.csv", csv.toByteArray(Charsets.UTF_8))
        }
    }

    fun showMessage(msg: String) { _uiState.update { it.copy(snackbarMessage = msg) } }
    fun clearSnackbar() { _uiState.update { it.copy(snackbarMessage = null) } }

    private fun loadAnalyticsAndMonthly() {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val (analytics, monthly) = withContext(Dispatchers.IO) {
                engine.getClassAnalytics(cls.major, cls.grade, cls.section) to
                    engine.getMonthlyReport(cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth)
            }
            _uiState.update { it.copy(classAnalytics = analytics, monthlyReport = monthly) }
        }
    }

    private fun loadAttendanceSnapshot() {
        val st = _uiState.value
        val cls = st.selectedClass
        if (cls == null) {
            _uiState.update {
                it.copy(isLoading = false, students = emptyList(), isPeriodSaved = false, summary = PeriodSummary(0, 0, 0, 0, 0, 0), jalaliDate = engine.formatJalaliDate(st.selectedDate.toString()))
            }
            return
        }
        viewModelScope.launch {
            val snap = withContext(Dispatchers.IO) {
                engine.getClassAttendance(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod, st.searchQuery)
            }
            _uiState.update { it.copy(isLoading = false, jalaliDate = snap.jalaliDate, isPeriodSaved = snap.isPeriodSaved, summary = snap.summary, students = snap.students) }
        }
    }
}
