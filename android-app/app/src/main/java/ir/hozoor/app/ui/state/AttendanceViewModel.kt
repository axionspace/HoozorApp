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
import uniffi.hozoor_core.ClassGroup
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
    val schoolName: String = "هنرستان شهید آوینی",
    val classes: List<ClassGroup> = emptyList(),
    val selectedClass: ClassGroup? = null,
    val selectedDate: LocalDate = LocalDate.now(),
    val jalaliDate: String = "",
    val selectedPeriod: Period = Period.FIRST,
    val searchQuery: String = "",
    val students: List<StudentAttendanceRow> = emptyList(),
    val summary: PeriodSummary = PeriodSummary(0, 0, 0, 0, 0, 0),
    val principalPhone: String = "",
    val principalReport: PrincipalReportBundle? = null,
    val reportWholeSchool: Boolean = false,
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
            val savedPhone = withContext(Dispatchers.IO) { engine.getPrincipalPhone() }
            val ym = engine.getJalaliYearMonth(LocalDate.now().toString())
            _uiState.update {
                it.copy(
                    principalPhone = savedPhone,
                    monthlyYear = ym.year,
                    monthlyMonth = ym.month
                )
            }
            refreshClassesAndData()
        }
    }

    fun switchTab(tabIndex: Int) {
        _uiState.update { it.copy(activeTab = tabIndex) }
        if (tabIndex == 1) loadMonthlyReport()
    }

    fun refreshClassesAndData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val classes = withContext(Dispatchers.IO) { engine.getClasses() }
            val currentSelected = _uiState.value.selectedClass
            val activeClass = classes.find {
                it.major == currentSelected?.major &&
                    it.grade == currentSelected?.grade &&
                    it.section == currentSelected?.section
            } ?: classes.firstOrNull()

            _uiState.update {
                it.copy(
                    classes = classes,
                    selectedClass = activeClass,
                    schoolName = activeClass?.schoolName ?: it.schoolName,
                    jalaliDate = engine.formatJalaliDate(it.selectedDate.toString())
                )
            }
            loadAttendanceSnapshot()
            if (_uiState.value.activeTab == 1) loadMonthlyReport()
        }
    }

    fun selectPeriod(period: Period) {
        if (_uiState.value.selectedPeriod == period) return
        _uiState.update { it.copy(selectedPeriod = period) }
        loadAttendanceSnapshot()
    }

    fun selectClass(group: ClassGroup) {
        _uiState.update { it.copy(selectedClass = group, schoolName = group.schoolName) }
        loadAttendanceSnapshot()
        if (_uiState.value.activeTab == 1) loadMonthlyReport()
    }

    fun shiftDate(days: Long) {
        _uiState.update { it.copy(selectedDate = it.selectedDate.plusDays(days)) }
        loadAttendanceSnapshot()
    }

    fun shiftJalaliMonth(delta: Int) {
        val cur = _uiState.value
        var y = cur.monthlyYear
        var m = cur.monthlyMonth + delta
        if (m > 12) { m = 1; y += 1 }
        if (m < 1) { m = 12; y -= 1 }
        _uiState.update { it.copy(monthlyYear = y, monthlyMonth = m) }
        loadMonthlyReport()
    }

    fun toggleMonthlySort() {
        _uiState.update { it.copy(sortMonthlyByAbsence = !it.sortMonthlyByAbsence) }
    }

    fun updateSearch(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
        loadAttendanceSnapshot()
    }

    fun setStudentStatus(studentId: Long, status: AttendanceStatus) {
        val state = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setAttendance(studentId, state.selectedDate.toString(), state.selectedPeriod, status, "")
            }
            loadAttendanceSnapshot()
        }
    }

    fun markRemainingPresent() {
        val state = _uiState.value
        val group = state.selectedClass ?: return
        viewModelScope.launch {
            val count = withContext(Dispatchers.IO) {
                engine.markClassStatus(
                    group.major, group.grade, group.section,
                    state.selectedDate.toString(), state.selectedPeriod,
                    AttendanceStatus.PRESENT, true
                )
            }
            loadAttendanceSnapshot()
            showMessage("وضعیت حاضر برای $count دانش‌آموز ثبت شد")
        }
    }

    fun copyFromPreviousPeriod() {
        val state = _uiState.value
        val group = state.selectedClass ?: return
        if (state.selectedPeriod == Period.FIRST) {
            showMessage("زنگ اول، زنگ قبلی ندارد")
            return
        }
        viewModelScope.launch {
            val copied = withContext(Dispatchers.IO) {
                engine.copyFromPreviousPeriod(
                    group.major, group.grade, group.section,
                    state.selectedDate.toString(), state.selectedPeriod
                )
            }
            loadAttendanceSnapshot()
            showMessage(if (copied > 0) "وضعیت $copied نفر از زنگ قبل کپی شد" else "در زنگ قبل موردی ثبت نشده است")
        }
    }

    fun importFileBytes(fileName: String, bytes: ByteArray, replaceExisting: Boolean = false) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val report = withContext(Dispatchers.IO) {
                    engine.importFileBytes(fileName, bytes, replaceExisting)
                }
                refreshClassesAndData()
                showMessage("${report.importedCount} دانش‌آموز در ${report.classesCount} کلاس وارد شد")
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false) }
                showMessage("خطا در خواندن فایل: ${e.message}")
            }
        }
    }

    fun preparePrincipalReport(wholeSchool: Boolean = _uiState.value.reportWholeSchool) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        _uiState.update { it.copy(reportWholeSchool = wholeSchool) }
        viewModelScope.launch {
            val bundle = withContext(Dispatchers.IO) {
                engine.generatePrincipalReport(cls.major, cls.grade, cls.section, state.selectedDate.toString(), wholeSchool)
            }
            _uiState.update { it.copy(principalReport = bundle) }
        }
    }

    fun updatePrincipalPhone(phone: String) {
        _uiState.update { it.copy(principalPhone = phone) }
        viewModelScope.launch(Dispatchers.IO) { engine.savePrincipalPhone(phone) }
    }

    fun exportDailyExcel(wholeSchool: Boolean, onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) {
                engine.exportDailyXlsx(cls.major, cls.grade, cls.section, state.selectedDate.toString(), wholeSchool)
            }
            val prefix = if (wholeSchool) "hozoor_school" else "hozoor_${cls.major}_${cls.grade}_${cls.section}"
            onReady("${prefix}_${state.selectedDate}.xlsx", bytes)
        }
    }

    fun exportCurrentClassCsv(onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) {
                engine.exportDailyCsv(cls.major, cls.grade, cls.section, state.selectedDate.toString())
            }
            onReady("hozoor_${cls.major}_${cls.grade}_${cls.section}_${state.selectedDate}.csv", csv.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportMonthlyExcel(onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) {
                engine.exportMonthlyXlsx(cls.major, cls.grade, cls.section, state.monthlyYear, state.monthlyMonth)
            }
            onReady("monthly_${cls.major}_${cls.grade}_${cls.section}_${state.monthlyYear}_${state.monthlyMonth}.xlsx", bytes)
        }
    }

    fun exportMonthlyCsv(onReady: (String, ByteArray) -> Unit) {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) {
                engine.exportMonthlyCsv(cls.major, cls.grade, cls.section, state.monthlyYear, state.monthlyMonth)
            }
            onReady(
                "monthly_${cls.major}_${cls.grade}_${cls.section}_${state.monthlyYear}_${state.monthlyMonth}.csv",
                csv.toByteArray(Charsets.UTF_8)
            )
        }
    }

    fun showMessage(msg: String) {
        _uiState.update { it.copy(snackbarMessage = msg) }
    }

    fun clearSnackbar() {
        _uiState.update { it.copy(snackbarMessage = null) }
    }

    private fun loadMonthlyReport() {
        val state = _uiState.value
        val cls = state.selectedClass ?: return
        viewModelScope.launch {
            val report = withContext(Dispatchers.IO) {
                engine.getMonthlyReport(cls.major, cls.grade, cls.section, state.monthlyYear, state.monthlyMonth)
            }
            _uiState.update { it.copy(monthlyReport = report) }
        }
    }

    private fun loadAttendanceSnapshot() {
        val state = _uiState.value
        val group = state.selectedClass
        if (group == null) {
            _uiState.update {
                it.copy(
                    isLoading = false,
                    students = emptyList(),
                    summary = PeriodSummary(0, 0, 0, 0, 0, 0),
                    jalaliDate = engine.formatJalaliDate(state.selectedDate.toString())
                )
            }
            return
        }
        viewModelScope.launch {
            val snap = withContext(Dispatchers.IO) {
                engine.getClassAttendance(
                    group.major, group.grade, group.section,
                    state.selectedDate.toString(), state.selectedPeriod, state.searchQuery
                )
            }
            _uiState.update {
                it.copy(
                    isLoading = false,
                    jalaliDate = snap.jalaliDate,
                    summary = snap.summary,
                    students = snap.students
                )
            }
        }
    }
}
