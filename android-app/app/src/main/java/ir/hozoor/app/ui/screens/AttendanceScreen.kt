package ir.hozoor.app.ui.screens

import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CalendarMonth
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.DarkMode
import androidx.compose.material.icons.rounded.ExpandLess
import androidx.compose.material.icons.rounded.ExpandMore
import androidx.compose.material.icons.rounded.LightMode
import androidx.compose.material.icons.rounded.Palette
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LoadingIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ir.hozoor.app.ui.components.ClassCategorySelector
import ir.hozoor.app.ui.components.ExportAndReportSheet
import ir.hozoor.app.ui.components.ExpressiveAttendanceToolbar
import ir.hozoor.app.ui.components.JalaliDatePickerDialog
import ir.hozoor.app.ui.components.PeriodSelector
import ir.hozoor.app.ui.components.QuickScoreDialog
import ir.hozoor.app.ui.components.StudentAttendanceCard
import ir.hozoor.app.ui.components.StudentEditDialog
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.state.AttendanceViewModel
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.util.FileShareHelper
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.StudentAttendanceRow

private val IMPORT_MIME_TYPES = arrayOf(
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "text/csv",
    "text/comma-separated-values",
    "application/csv",
    "text/plain"
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class, ExperimentalMaterial3Api::class)
@Composable
fun AttendanceScreen(viewModel: AttendanceViewModel, isDarkTheme: Boolean) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }

    var showExportSheet by remember { mutableStateOf(false) }
    var showDatePicker by remember { mutableStateOf(false) }
    var showTeacherPanel by remember { mutableStateOf(false) }
    var showAddDialog by remember { mutableStateOf(false) }
    var editingStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var scoringStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var deletingStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var showDeleteClassDialog by remember { mutableStateOf(false) }
    var pendingBackupBytes by remember { mutableStateOf<ByteArray?>(null) }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri ?: return@rememberLauncherForActivityResult
        val name = FileShareHelper.resolveFileName(context, uri)
        context.contentResolver.openInputStream(uri)?.use { stream ->
            viewModel.importFileBytes(fileName = name, bytes = stream.readBytes(), replaceExisting = true)
        }
    }

    val saveBackupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri: Uri? ->
        val bytes = pendingBackupBytes
        pendingBackupBytes = null
        if (uri != null && bytes != null) {
            runCatching {
                context.contentResolver.openOutputStream(uri)?.use { it.write(bytes) }
                viewModel.showMessage("فایل پشتیبان کامل با موفقیت در گوشی ذخیره شد")
            }.onFailure { viewModel.showMessage("خطا در ذخیره پشتیبان") }
        }
    }

    val backupRestorePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri ?: return@rememberLauncherForActivityResult
        context.contentResolver.openInputStream(uri)?.use { stream ->
            viewModel.restoreBackupJson(stream.bufferedReader(Charsets.UTF_8).readText())
        }
    }

    LaunchedEffect(state.snackbarMessage) {
        state.snackbarMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }, containerColor = MaterialTheme.colorScheme.background) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            Column(modifier = Modifier.fillMaxSize()) {
                // هدر عمومی + نام آموزشگاه از فایل ورودی + Dynamic Color + تاریک/روشن
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = state.selectedClass?.schoolName?.ifBlank { "سامانه حضور و غیاب" } ?: "سامانه حضور و غیاب",
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.ExtraBold
                        )
                        Text(state.jalaliDate, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        FilledTonalIconButton(onClick = viewModel::toggleDynamicColor) {
                            Icon(Icons.Rounded.Palette, "رنگ پویا", tint = if (state.dynamicColorEnabled) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Spacer(Modifier.width(4.dp))
                    }
                    FilledTonalIconButton(onClick = { viewModel.toggleDarkMode(isDarkTheme) }) {
                        Icon(if (isDarkTheme) Icons.Rounded.LightMode else Icons.Rounded.DarkMode, "حالت تاریک یا روشن")
                    }
                }

                // نوار تقویم شمسی و پنل مشخصات دبیر/درس
                Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    FilledTonalButton(onClick = { showDatePicker = true }, contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp), modifier = Modifier.weight(1f)) {
                        Icon(Icons.Rounded.CalendarMonth, null, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("تقویم شمسی", maxLines = 1)
                    }
                    IconButton(onClick = { viewModel.shiftDate(-1) }) { Icon(Icons.Rounded.ChevronRight, "روز قبل") }
                    IconButton(onClick = { viewModel.shiftDate(1) }) { Icon(Icons.Rounded.ChevronLeft, "روز بعد") }
                    OutlinedButton(onClick = { showTeacherPanel = !showTeacherPanel }, contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)) {
                        Text("دبیر و درس")
                        Icon(if (showTeacherPanel) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, null)
                    }
                }

                AnimatedVisibility(visible = showTeacherPanel) {
                    Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp), shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainerLow) {
                        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(value = state.teacherName, onValueChange = viewModel::updateTeacherName, label = { Text("نام دبیر") }, singleLine = true, modifier = Modifier.weight(1f))
                                OutlinedTextField(value = state.lessonName, onValueChange = viewModel::updateLessonName, label = { Text("نام درس") }, singleLine = true, modifier = Modifier.weight(1f))
                            }
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(value = state.principalPhone, onValueChange = viewModel::updatePrincipalPhone, label = { Text("موبایل مدیر") }, singleLine = true, modifier = Modifier.weight(1.4f))
                                OutlinedTextField(value = state.classTime, onValueChange = viewModel::updateClassTime, label = { Text("ساعت") }, singleLine = true, modifier = Modifier.weight(0.8f))
                            }
                        }
                    }
                }

                if (state.classes.isNotEmpty()) {
                    Row(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        FilterChip(selected = state.activeTab == 0, onClick = { viewModel.switchTab(0) }, label = { Text("حضور و غیاب روزانه") }, modifier = Modifier.weight(1f))
                        FilterChip(selected = state.activeTab == 1, onClick = { viewModel.switchTab(1) }, label = { Text("آمار و گزارش ماهانه") }, modifier = Modifier.weight(1f))
                    }
                }

                when {
                    state.isLoading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { LoadingIndicator() }
                    state.classes.isEmpty() -> EmptyImportState(
                        onImportClick = { filePicker.launch(IMPORT_MIME_TYPES) },
                        onLoadSampleClick = {
                            runCatching {
                                context.assets.open("sample_school.csv").use { s ->
                                    viewModel.importFileBytes("sample_school.csv", s.readBytes(), true)
                                }
                            }
                        },
                        onDownloadTemplate = {
                            viewModel.exportTemplateExcel { name, bytes ->
                                FileShareHelper.shareBytesAsFile(context, name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", bytes, "فایل نمونه Excel")
                            }
                        },
                        onRestoreBackup = { backupRestorePicker.launch(arrayOf("application/json", "text/plain", "*/*")) }
                    )
                    else -> {
                        AnimatedContent(
                            targetState = state.activeTab,
                            transitionSpec = { fadeIn(tween(220)) togetherWith fadeOut(tween(180)) },
                            label = "tabSwitch"
                        ) { tab ->
                            if (tab == 1) {
                                MonthlyReportContent(
                                    majors = state.majors,
                                    selectedMajor = state.selectedMajor,
                                    grades = state.gradesForSelection,
                                    selectedGrade = state.selectedGrade,
                                    sections = state.sectionsForSelection,
                                    selectedSection = state.selectedSection,
                                    onSelectMajor = viewModel::selectMajor,
                                    onSelectGrade = viewModel::selectGrade,
                                    onSelectSection = viewModel::selectSection,
                                    analytics = state.classAnalytics,
                                    report = state.monthlyReport,
                                    sortByAbsence = state.sortMonthlyByAbsence,
                                    onShiftMonth = viewModel::shiftJalaliMonth,
                                    onToggleSort = viewModel::toggleMonthlySort,
                                    onExportExcel = {
                                        viewModel.exportMonthlyExcel { name, bytes ->
                                            FileShareHelper.shareBytesAsFile(context, name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", bytes, "خروجی اکسل ماهانه")
                                        }
                                    },
                                    onExportCsv = {
                                        viewModel.exportMonthlyCsv { name, bytes ->
                                            FileShareHelper.shareBytesAsFile(context, name, "text/csv", bytes, "خروجی CSV ماهانه")
                                        }
                                    },
                                    onRequestDeleteClass = { showDeleteClassDialog = true }
                                )
                            } else {
                                LazyColumn(modifier = Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 104.dp, top = 2.dp)) {
                                    item(key = "category_grid") {
                                        ClassCategorySelector(
                                            majors = state.majors,
                                            selectedMajor = state.selectedMajor,
                                            grades = state.gradesForSelection,
                                            selectedGrade = state.selectedGrade,
                                            sections = state.sectionsForSelection,
                                            selectedSection = state.selectedSection,
                                            onSelectMajor = viewModel::selectMajor,
                                            onSelectGrade = viewModel::selectGrade,
                                            onSelectSection = viewModel::selectSection
                                        )
                                    }
                                    item(key = "period_and_search") {
                                        Spacer(Modifier.height(6.dp))
                                        PeriodSelector(selectedPeriod = state.selectedPeriod, onSelectPeriod = viewModel::selectPeriod)
                                        SummaryHeaderCard(summary = state.summary)
                                        OutlinedTextField(
                                            value = state.searchQuery,
                                            onValueChange = viewModel::updateSearch,
                                            placeholder = { Text("جستجوی نام، نام خانوادگی، پدر یا کد ملی...") },
                                            leadingIcon = { Icon(Icons.Rounded.Search, null) },
                                            singleLine = true,
                                            shape = RoundedCornerShape(22.dp),
                                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                                        )
                                    }
                                    itemsIndexed(items = state.students, key = { _, s -> s.studentId }, contentType = { _, _ -> "student" }) { idx, student ->
                                        StudentAttendanceCard(
                                            indexInClass = idx + 1,
                                            student = student,
                                            selectedPeriod = state.selectedPeriod,
                                            onStatusChange = { viewModel.setStudentStatus(student.studentId, it) },
                                            onCyclePeriodDot = { pIdx -> viewModel.cycleStudentPeriodStatus(student, pIdx) },
                                            onCallParent = { phone -> context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone"))) },
                                            onQuickScore = { scoringStudent = it },
                                            onSendIndividualNotice = { s, status ->
                                                val statusText = if (status == AttendanceStatus.LATE) "با تأخیر حاضر شده است" else "غایب بوده است"
                                                val pTitle = when (state.selectedPeriod) {
                                                    Period.FIRST -> "زنگ اول"
                                                    Period.SECOND -> "زنگ دوم"
                                                    Period.THIRD -> "زنگ سوم"
                                                    Period.FOURTH -> "زنگ چهارم"
                                                }
                                                val clsDesc = buildString {
                                                    append("پایه ${state.selectedGrade} شعبه ${toPersianDigits(state.selectedSection.toString())}")
                                                    if (state.selectedMajor.isNotBlank()) append(" رشته ${state.selectedMajor}")
                                                }
                                                val lessonDesc = if (state.lessonName.isNotBlank()) "در درس ${state.lessonName} " else ""
                                                val teacherDesc = if (state.teacherName.isNotBlank()) " با دبیر ${state.teacherName}" else ""
                                                val body = "سلام علیکم، دانش‌آموز ${s.firstName} ${s.lastName}، فرزند ${s.fatherName.ifBlank { "ثبت نشده" }}، $clsDesc، ${lessonDesc}مورخه ${state.jalaliDate} ($pTitle ساعت ${toPersianDigits(state.classTime)})$teacherDesc $statusText."
                                                val targetPhone = state.principalPhone.ifBlank { s.mobile }
                                                FileShareHelper.openSmsApp(context, targetPhone, body)
                                            },
                                            onEditStudent = { editingStudent = it },
                                            onDeleteStudent = { deletingStudent = it }
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (state.activeTab == 0 && state.classes.isNotEmpty()) {
                ExpressiveAttendanceToolbar(
                    selectedPeriod = state.selectedPeriod,
                    onResetAllPresent = viewModel::resetAllToPresent,
                    onCopyFromPrevious = viewModel::copyFromPreviousPeriod,
                    onAddStudent = { showAddDialog = true },
                    onOpenExportSheet = {
                        viewModel.prepareExportSheet(false)
                        showExportSheet = true
                    },
                    onImportFile = { filePicker.launch(IMPORT_MIME_TYPES) },
                    modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp)
                )
            }
        }
    }

    if (showDatePicker) {
        val ym = remember(state.selectedDate) { viewModel.currentDateJalaliYearMonth() }
        JalaliDatePickerDialog(ym.year, ym.month, state.selectedDate.toString(), viewModel::getJalaliCalendarGrid, viewModel::selectDateIso) { showDatePicker = false }
    }
    if (showAddDialog) {
        StudentEditDialog(null, { f, l, fa, nid, mob, sc -> viewModel.addStudentToCurrentClass(f, l, fa, nid, mob, sc) }) { showAddDialog = false }
    }
    editingStudent?.let { st ->
        StudentEditDialog(st, { f, l, fa, nid, mob, sc -> viewModel.updateStudent(st.studentId, f, l, fa, nid, mob, sc) }) { editingStudent = null }
    }
    scoringStudent?.let { st ->
        QuickScoreDialog(st, { sc -> viewModel.saveStudentScore(st.studentId, sc) }) { scoringStudent = null }
    }
    deletingStudent?.let { st ->
        AlertDialog(
            onDismissRequest = { deletingStudent = null },
            title = { Text("حذف دانش‌آموز") },
            text = { Text("آیا «${st.firstName} ${st.lastName}» و تمام سوابق او حذف شوند؟") },
            confirmButton = { TextButton(onClick = { viewModel.deleteStudent(st.studentId); deletingStudent = null }) { Text("حذف", color = MaterialTheme.colorScheme.error) } },
            dismissButton = { TextButton(onClick = { deletingStudent = null }) { Text("انصراف") } }
        )
    }
    if (showDeleteClassDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteClassDialog = false },
            title = { Text("حذف کامل کلاس") },
            text = { Text("تمام دانش‌آموزان و سوابق این کلاس حذف می‌شوند. آیا مطمئن هستید؟") },
            confirmButton = { TextButton(onClick = { viewModel.deleteCurrentClass(); showDeleteClassDialog = false }) { Text("حذف کلاس", color = MaterialTheme.colorScheme.error) } },
            dismissButton = { TextButton(onClick = { showDeleteClassDialog = false }) { Text("انصراف") } }
        )
    }

    if (showExportSheet) {
        ExportAndReportSheet(
            report = state.principalReport,
            summary = state.summary,
            backupStats = state.backupStats,
            wholeSchool = state.reportWholeSchool,
            principalPhone = state.principalPhone,
            feedbackMessage = state.sheetFeedback,
            onToggleWholeSchool = { viewModel.prepareExportSheet(it) },
            onPrincipalPhoneChange = viewModel::updatePrincipalPhone,
            onSendSms = { phone, sms ->
                if (!FileShareHelper.openSmsApp(context, phone, sms)) {
                    viewModel.setSheetFeedback("برنامه پیامک باز نشد؛ متن را کپی کنید.")
                }
            },
            onShareText = { txt -> FileShareHelper.shareText(context, txt, "ارسال گزارش به مدیر") },
            onCopyText = { txt ->
                FileShareHelper.copyToClipboard(context, "گزارش مدیر", txt)
                viewModel.showMessage("متن گزارش کپی شد")
                showExportSheet = false
            },
            onSendGroupPeriodSms = { status ->
                viewModel.generatePeriodGroupMessage(status) { msg ->
                    if (!FileShareHelper.openSmsApp(context, state.principalPhone, msg)) {
                        viewModel.setSheetFeedback("برنامه پیامک در این گوشی پیدا نشد.")
                    }
                }
            },
            onSendGroupPeriodShare = { status ->
                viewModel.generatePeriodGroupMessage(status) { msg ->
                    FileShareHelper.shareText(context, msg, "ارسال پیام گروهی به مدیر")
                }
            },
            onExportExcel = {
                viewModel.exportDailyExcel(state.reportWholeSchool) { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", bytes, "خروجی اکسل")
                }
            },
            onExportCsv = {
                viewModel.exportCurrentClassCsv { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "text/csv", bytes, "خروجی CSV")
                }
            },
            onExportTemplateExcel = {
                viewModel.exportTemplateExcel { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", bytes, "فایل نمونه Excel")
                }
            },
            onSaveBackupToDevice = {
                viewModel.exportBackupJson { name, bytes ->
                    pendingBackupBytes = bytes
                    saveBackupLauncher.launch(name)
                }
            },
            onShareBackupJson = {
                viewModel.exportBackupJson { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "application/json", bytes, "پشتیبان کامل (JSON)")
                }
            },
            onRestoreBackupJson = {
                showExportSheet = false
                backupRestorePicker.launch(arrayOf("application/json", "text/plain", "*/*"))
            },
            onDismiss = { showExportSheet = false }
        )
    }
}

@Composable
private fun SummaryHeaderCard(summary: PeriodSummary) {
    Surface(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp), shape = RoundedCornerShape(20.dp), color = MaterialTheme.colorScheme.surfaceContainer) {
        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 10.dp, horizontal = 12.dp), horizontalArrangement = Arrangement.SpaceBetween) {
            MetricPill("کل", summary.total, MaterialTheme.colorScheme.primary)
            MetricPill("حاضر", summary.present, StatusColors.Present)
            MetricPill("غایب", summary.absent, StatusColors.Absent)
            MetricPill("تأخیر", summary.late, StatusColors.Late)
            MetricPill("موجه", summary.excused, StatusColors.Excused)
        }
    }
}

@Composable
private fun MetricPill(label: String, count: Int, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(toPersianDigits(count.toString()), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun EmptyImportState(
    onImportClick: () -> Unit,
    onLoadSampleClick: () -> Unit,
    onDownloadTemplate: () -> Unit,
    onRestoreBackup: () -> Unit
) {
    Column(modifier = Modifier.fillMaxSize().padding(32.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text("سامانه حضور و غیاب آماده است", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold)
        Spacer(Modifier.height(8.dp))
        Text("فایل اکسل (.xlsx) یا CSV را وارد کنید تا کلاس‌ها بر اساس رشته، پایه و شعبه دسته‌بندی شوند.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(20.dp))
        Button(onClick = onImportClick, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Rounded.UploadFile, null); Spacer(Modifier.width(8.dp)); Text("انتخاب فایل اکسل یا CSV")
        }
        Spacer(Modifier.height(8.dp))
        FilledTonalButton(onClick = onLoadSampleClick, modifier = Modifier.fillMaxWidth()) { Text("تست سریع با داده‌های نمونه") }
        Spacer(Modifier.height(8.dp))
        OutlinedButton(onClick = onDownloadTemplate, modifier = Modifier.fillMaxWidth()) { Text("دریافت فایل نمونه Excel (XLSX)") }
        Spacer(Modifier.height(8.dp))
        OutlinedButton(onClick = onRestoreBackup, modifier = Modifier.fillMaxWidth()) { Text("بازیابی از پشتیبان قبلی (JSON)") }
    }
}
