package ir.hozoor.app.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.LoadingIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import ir.hozoor.app.ui.components.ExportAndReportSheet
import ir.hozoor.app.ui.components.ExpressiveAttendanceToolbar
import ir.hozoor.app.ui.components.PeriodSelector
import ir.hozoor.app.ui.components.StudentAttendanceCard
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.state.AttendanceViewModel
import ir.hozoor.app.ui.theme.StatusColors
import ir.hozoor.app.util.FileShareHelper
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary

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
fun AttendanceScreen(viewModel: AttendanceViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val snackbarHostState = remember { SnackbarHostState() }
    var showExportSheet by remember { mutableStateOf(false) }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri ?: return@rememberLauncherForActivityResult
        val name = FileShareHelper.resolveFileName(context, uri)
        context.contentResolver.openInputStream(uri)?.use { stream ->
            viewModel.importFileBytes(fileName = name, bytes = stream.readBytes(), replaceExisting = false)
        }
    }

    LaunchedEffect(state.snackbarMessage) {
        state.snackbarMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.clearSnackbar()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            Column(modifier = Modifier.fillMaxSize()) {
                // هدر مدرسه و تاریخ شمسی
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(state.schoolName, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold)
                        Text(state.jalaliDate, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                    }
                    if (state.activeTab == 0) {
                        IconButton(onClick = { viewModel.shiftDate(-1) }) {
                            Icon(Icons.Rounded.ChevronRight, contentDescription = "روز قبل")
                        }
                        IconButton(onClick = { viewModel.shiftDate(1) }) {
                            Icon(Icons.Rounded.ChevronLeft, contentDescription = "روز بعد")
                        }
                    }
                }

                // تب‌های روزانه و ماهانه
                if (state.classes.isNotEmpty()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        FilterChip(
                            selected = state.activeTab == 0,
                            onClick = { viewModel.switchTab(0) },
                            label = { Text("حضور و غیاب روزانه") },
                            modifier = Modifier.weight(1f)
                        )
                        FilterChip(
                            selected = state.activeTab == 1,
                            onClick = { viewModel.switchTab(1) },
                            label = { Text("گزارش ماهانه") },
                            modifier = Modifier.weight(1f)
                        )
                    }

                    // لیست کلاس‌ها
                    LazyRow(
                        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 4.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(items = state.classes, key = { "${it.major}_${it.grade}_${it.section}" }) { cls ->
                            FilterChip(
                                selected = cls == state.selectedClass,
                                onClick = { viewModel.selectClass(cls) },
                                label = {
                                    Text("${cls.major} • ${cls.grade} ${toPersianDigits(cls.section.toString())} (${toPersianDigits(cls.studentCount.toString())})")
                                }
                            )
                        }
                    }
                }

                when {
                    state.isLoading -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                            LoadingIndicator()
                        }
                    }
                    state.classes.isEmpty() -> {
                        EmptyImportState(
                            onImportClick = { filePicker.launch(IMPORT_MIME_TYPES) },
                            onLoadSampleClick = {
                                runCatching {
                                    context.assets.open("sample_avini.csv").use { s ->
                                        viewModel.importFileBytes("sample_avini.csv", s.readBytes(), true)
                                    }
                                }
                            }
                        )
                    }
                    state.activeTab == 1 -> {
                        MonthlyReportContent(
                            report = state.monthlyReport,
                            sortByAbsence = state.sortMonthlyByAbsence,
                            onShiftMonth = viewModel::shiftJalaliMonth,
                            onToggleSort = viewModel::toggleMonthlySort,
                            onExportExcel = {
                                viewModel.exportMonthlyExcel { name, bytes ->
                                    FileShareHelper.shareBytesAsFile(
                                        context, name,
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        bytes, "خروجی اکسل ماهانه"
                                    )
                                }
                            },
                            onExportCsv = {
                                viewModel.exportMonthlyCsv { name, bytes ->
                                    FileShareHelper.shareBytesAsFile(context, name, "text/csv", bytes, "خروجی CSV ماهانه")
                                }
                            }
                        )
                    }
                    else -> {
                        Spacer(Modifier.height(4.dp))
                        PeriodSelector(selectedPeriod = state.selectedPeriod, onSelectPeriod = viewModel::selectPeriod)
                        SummaryHeaderCard(summary = state.summary)
                        OutlinedTextField(
                            value = state.searchQuery,
                            onValueChange = viewModel::updateSearch,
                            placeholder = { Text("جستجوی نام، نام خانوادگی یا کد ملی...") },
                            leadingIcon = { Icon(Icons.Rounded.Search, contentDescription = null) },
                            singleLine = true,
                            shape = RoundedCornerShape(24.dp),
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                        )

                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(bottom = 96.dp, top = 4.dp)
                        ) {
                            itemsIndexed(items = state.students, key = { _, s -> s.studentId }, contentType = { _, _ -> "student" }) { idx, student ->
                                StudentAttendanceCard(
                                    indexInClass = idx + 1,
                                    student = student,
                                    onStatusChange = { viewModel.setStudentStatus(student.studentId, it) },
                                    onCallParent = { phone ->
                                        context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone")))
                                    },
                                    onSendSms = { s ->
                                        val pTitle = when (state.selectedPeriod) {
                                            Period.FIRST -> "زنگ اول"
                                            Period.SECOND -> "زنگ دوم"
                                            Period.THIRD -> "زنگ سوم"
                                            Period.FOURTH -> "زنگ چهارم"
                                        }
                                        val body = "با سلام، ولی محترم دانش‌آموز ${s.firstName} ${s.lastName}؛ " +
                                            "ایشان در تاریخ ${state.jalaliDate} ($pTitle) در ${state.schoolName} غایب/دارای تأخیر بوده‌اند."
                                        FileShareHelper.openSmsApp(context, s.mobile, body)
                                    }
                                )
                            }
                        }
                    }
                }
            }

            if (state.activeTab == 0 && state.classes.isNotEmpty()) {
                ExpressiveAttendanceToolbar(
                    selectedPeriod = state.selectedPeriod,
                    onMarkRemainingPresent = viewModel::markRemainingPresent,
                    onCopyFromPrevious = viewModel::copyFromPreviousPeriod,
                    onOpenExportSheet = {
                        viewModel.preparePrincipalReport(false)
                        showExportSheet = true
                    },
                    onImportFile = { filePicker.launch(IMPORT_MIME_TYPES) },
                    modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 16.dp)
                )
            }
        }
    }

    if (showExportSheet) {
        ExportAndReportSheet(
            report = state.principalReport,
            wholeSchool = state.reportWholeSchool,
            principalPhone = state.principalPhone,
            onToggleWholeSchool = { viewModel.preparePrincipalReport(it) },
            onPrincipalPhoneChange = viewModel::updatePrincipalPhone,
            onSendSms = { phone, sms -> FileShareHelper.openSmsApp(context, phone, sms) },
            onShareText = { txt -> FileShareHelper.shareText(context, txt, "ارسال گزارش به مدیر") },
            onCopyText = { txt ->
                FileShareHelper.copyToClipboard(context, "گزارش مدیر", txt)
                viewModel.showMessage("متن گزارش کپی شد")
                showExportSheet = false
            },
            onExportExcel = {
                viewModel.exportDailyExcel(state.reportWholeSchool) { name, bytes ->
                    FileShareHelper.shareBytesAsFile(
                        context, name,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        bytes, "خروجی اکسل حضور و غیاب"
                    )
                }
            },
            onExportCsv = {
                viewModel.exportCurrentClassCsv { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "text/csv", bytes, "خروجی CSV حضور و غیاب")
                }
            },
            onDismiss = { showExportSheet = false }
        )
    }
}

@Composable
private fun SummaryHeaderCard(summary: PeriodSummary) {
    val marked = summary.total - summary.unmarked
    val progress = if (summary.total > 0) marked.toFloat() / summary.total else 0f
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainer
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                MetricPill("حاضر", summary.present, StatusColors.Present)
                MetricPill("غایب", summary.absent, StatusColors.Absent)
                MetricPill("تأخیر", summary.late, StatusColors.Late)
                MetricPill("موجه", summary.excused, StatusColors.Excused)
                MetricPill("باقیمانده", summary.unmarked, StatusColors.Unmarked)
            }
            Spacer(Modifier.height(8.dp))
            LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth().height(6.dp))
        }
    }
}

@Composable
private fun MetricPill(label: String, count: Int, color: androidx.compose.ui.graphics.Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(toPersianDigits(count.toString()), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun EmptyImportState(onImportClick: () -> Unit, onLoadSampleClick: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("لیست دانش‌آموزان خالی است", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(8.dp))
        Text(
            text = "فایل اکسل (.xlsx) یا CSV مدرسه را انتخاب کنید تا در چند میلی‌ثانیه کلاس‌بندی شود.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(20.dp))
        Button(onClick = onImportClick) {
            Icon(Icons.Rounded.UploadFile, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("انتخاب فایل اکسل یا CSV")
        }
        Spacer(Modifier.height(10.dp))
        FilledTonalButton(onClick = onLoadSampleClick) {
            Text("تست سریع با نمونه هنرستان شهید آوینی")
        }
    }
}
