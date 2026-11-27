from pathlib import Path

FILES = {
    "android-app/settings.gradle.kts": r'''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "HozoorApp"
include(":app")
''',

    "android-app/build.gradle.kts": r'''plugins {
    id("com.android.application") version "8.9.1" apply false
    id("org.jetbrains.kotlin.android") version "2.1.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.20" apply false
}
''',

    "android-app/gradle.properties": r'''org.gradle.jvmargs=-Xmx3072m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
''',

    "android-app/app/proguard-rules.pro": r'''-keep class com.sun.jna.** { *; }
-keep class * implements com.sun.jna.** { *; }
-keep class uniffi.hozoor_core.** { *; }
-dontwarn java.awt.**
-dontwarn com.sun.jna.**
''',

    "android-app/app/build.gradle.kts": r'''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "ir.hozoor.app"
    compileSdk = 35

    defaultConfig {
        applicationId = "ir.hozoor.app"
        minSdk = 24
        targetSdk = 35
        versionCode = 2
        versionName = "2.0.0"
    }

    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_FILE") ?: "release.jks")
            storePassword = System.getenv("KEYSTORE_PASS") ?: "hozoor123456"
            keyAlias = System.getenv("KEY_ALIAS") ?: "hozoor"
            keyPassword = System.getenv("KEY_PASS") ?: "hozoor123456"
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    splits {
        abi {
            isEnable = true
            reset()
            include("arm64-v8a", "armeabi-v7a")
            isUniversalApk = true
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2025.05.00")
    implementation(composeBom)

    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.compose.material3:material3:1.4.0-alpha15")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.compose.ui:ui")

    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.9.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")

    implementation("net.java.dev.jna:jna:5.15.0@aar")
    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")
}
''',

    "android-app/app/src/main/AndroidManifest.xml": r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:name=".HozoorApplication"
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher_hozoor"
        android:label="حضور و غیاب"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
''',

    "android-app/app/src/main/res/xml/file_paths.xml": r'''<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="exports" path="exports/" />
</paths>
''',

    "android-app/app/src/main/res/drawable/ic_launcher_hozoor.xml": r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#146C56"
        android:pathData="M24,8 L84,8 C93,8 100,15 100,24 L100,84 C100,93 93,100 84,100 L24,100 C15,100 8,93 8,84 L8,24 C8,15 15,8 24,8 Z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M45,72 L27,54 L34,47 L45,58 L74,29 L81,36 Z" />
</vector>
''',

    "android-app/app/src/main/assets/sample_school.csv": r'''ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,دبیرستان نمونه,تجربی,دهم,1,علی,احمدی,حسن,1000000001,09121234501
2,دبیرستان نمونه,تجربی,دهم,1,رضا,رضایی,محمد,1000000002,09121234502
3,دبیرستان نمونه,تجربی,دهم,2,امیر,کریمی,مهدی,1000000003,09121234503
4,دبیرستان نمونه,ریاضی,یازدهم,1,حسین,موسوی,سعید,1000000004,09121234504
5,دبیرستان نمونه,ریاضی,دوازدهم,1,پارسا,رحیمی,بهرام,1000000005,09121234505
6,دبیرستان متوسطه اول,,هفتم,1,محمد,اکبری,مجید,1000000006,09121234506
7,دبیرستان متوسطه اول,,هشتم,1,طاها,جعفری,کریم,1000000007,09121234507
''',

    "android-app/app/src/main/java/ir/hozoor/app/HozoorApplication.kt": r'''package ir.hozoor.app

import android.app.Application
import uniffi.hozoor_core.AttendanceEngine
import java.io.File

class HozoorApplication : Application() {
    lateinit var engine: AttendanceEngine
        private set

    override fun onCreate() {
        super.onCreate()
        val dbFile = File(filesDir, "hozoor_attendance.db")
        engine = AttendanceEngine(dbFile.absolutePath)
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/MainActivity.kt": r'''package ir.hozoor.app

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import ir.hozoor.app.ui.screens.AttendanceScreen
import ir.hozoor.app.ui.state.AttendanceViewModel
import ir.hozoor.app.ui.theme.HozoorExpressiveTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = application as HozoorApplication

        setContent {
            val reduceMotion = remember {
                val am = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
                val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
                am.isLowRamDevice || pm.isPowerSaveMode || Build.VERSION.SDK_INT < Build.VERSION_CODES.P
            }

            val vm: AttendanceViewModel = viewModel(
                factory = object : ViewModelProvider.Factory {
                    @Suppress("UNCHECKED_CAST")
                    override fun <T : ViewModel> create(modelClass: Class<T>): T {
                        return AttendanceViewModel(app.engine) as T
                    }
                }
            )
            val uiState by vm.uiState.collectAsStateWithLifecycle()
            val systemDark = isSystemInDarkTheme()
            val useDark = when (uiState.themeMode) {
                "dark" -> true
                "light" -> false
                else -> systemDark
            }

            HozoorExpressiveTheme(
                darkTheme = useDark,
                dynamicColor = uiState.dynamicColorEnabled,
                reduceMotion = reduceMotion
            ) {
                AttendanceScreen(viewModel = vm, isDarkTheme = useDark)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/util/FileShareHelper.kt": r'''package ir.hozoor.app.util

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import java.io.File

object FileShareHelper {
    fun shareBytesAsFile(
        context: Context,
        fileName: String,
        mimeType: String,
        bytes: ByteArray,
        chooserTitle: String
    ) {
        val dir = File(context.cacheDir, "exports").apply { mkdirs() }
        val file = File(dir, fileName)
        file.writeBytes(bytes)
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)

        val intent = Intent(Intent.ACTION_SEND).apply {
            type = mimeType
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_SUBJECT, fileName)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, chooserTitle))
    }

    fun openSmsApp(context: Context, phone: String, body: String) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = Uri.parse("smsto:${phone.trim()}")
            putExtra("sms_body", body)
        }
        context.startActivity(intent)
    }

    fun shareText(context: Context, text: String, title: String) {
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
        }
        context.startActivity(Intent.createChooser(intent, title))
    }

    fun copyToClipboard(context: Context, label: String, text: String) {
        val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText(label, text))
    }

    fun resolveFileName(context: Context, uri: Uri): String {
        context.contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx >= 0 && cursor.moveToFirst()) {
                return cursor.getString(idx) ?: "students.xlsx"
            }
        }
        return "students.xlsx"
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/theme/Type.kt": r'''package ir.hozoor.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import ir.hozoor.app.R

val VazirmatnFontFamily = FontFamily(
    Font(R.font.vazirmatn_regular, FontWeight.Normal),
    Font(R.font.vazirmatn_medium, FontWeight.Medium),
    Font(R.font.vazirmatn_bold, FontWeight.Bold),
    Font(R.font.vazirmatn_extrabold, FontWeight.ExtraBold),
)

private val Base = Typography()

val HozoorTypography = Typography(
    displayLarge = Base.displayLarge.copy(fontFamily = VazirmatnFontFamily),
    displayMedium = Base.displayMedium.copy(fontFamily = VazirmatnFontFamily),
    displaySmall = Base.displaySmall.copy(fontFamily = VazirmatnFontFamily),
    headlineLarge = Base.headlineLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.ExtraBold),
    headlineMedium = Base.headlineMedium.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    headlineSmall = Base.headlineSmall.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleLarge = Base.titleLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleMedium = Base.titleMedium.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Bold),
    titleSmall = Base.titleSmall.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Medium),
    bodyLarge = Base.bodyLarge.copy(fontFamily = VazirmatnFontFamily),
    bodyMedium = Base.bodyMedium.copy(fontFamily = VazirmatnFontFamily),
    bodySmall = Base.bodySmall.copy(fontFamily = VazirmatnFontFamily),
    labelLarge = Base.labelLarge.copy(fontFamily = VazirmatnFontFamily, fontWeight = FontWeight.Medium),
    labelMedium = Base.labelMedium.copy(fontFamily = VazirmatnFontFamily),
    labelSmall = Base.labelSmall.copy(fontFamily = VazirmatnFontFamily),
)
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/theme/Theme.kt": r'''package ir.hozoor.app.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.MaterialExpressiveTheme
import androidx.compose.material3.MotionScheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.expressiveLightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection

object StatusColors {
    val Present = Color(0xFF15803D)
    val OnPresent = Color.White

    val Absent = Color(0xFFC62828)
    val OnAbsent = Color.White

    val Late = Color(0xFFEAB308)
    val OnLate = Color(0xFF1A1A1A)

    val Excused = Color(0xFF2563EB)
    val OnExcused = Color.White

    val Unmarked = Color(0xFF757982)
}

private val ExpressiveDarkFallback = darkColorScheme(
    primary = Color(0xFF4ADE80),
    onPrimary = Color(0xFF00391A),
    primaryContainer = Color(0xFF0F5132),
    onPrimaryContainer = Color(0xFFC2F7D4),
    secondary = Color(0xFF93C5FD),
    onSecondary = Color(0xFF003063),
    secondaryContainer = Color(0xFF1E3A5F),
    onSecondaryContainer = Color(0xFFD6E7FF),
    tertiary = Color(0xFFD8B4FE),
    onTertiary = Color(0xFF3B0764),
    tertiaryContainer = Color(0xFF4C1D95),
    onTertiaryContainer = Color(0xFFF3E8FF),
    background = Color(0xFF0F1412),
    surface = Color(0xFF0F1412),
    surfaceContainerLow = Color(0xFF171E1B),
    surfaceContainer = Color(0xFF1C2420),
    surfaceContainerHigh = Color(0xFF242E2A)
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun HozoorExpressiveTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    reduceMotion: Boolean = false,
    content: @Composable () -> Unit
) {
    val context = LocalContext.current
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> ExpressiveDarkFallback
        else -> expressiveLightColorScheme()
    }
    val motionScheme = if (reduceMotion) MotionScheme.standard() else MotionScheme.expressive()

    CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Rtl) {
        MaterialExpressiveTheme(
            colorScheme = colorScheme,
            motionScheme = motionScheme,
            typography = HozoorTypography,
            content = content
        )
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/state/AttendanceViewModel.kt": r'''package ir.hozoor.app.ui.state

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
    val schools: List<String> = emptyList(),
    val selectedSchool: String = "",
    val majorsForSchool: List<String> = emptyList(),
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
            val settings = withContext(Dispatchers.IO) {
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
                    teacherName = settings["teacher"].orEmpty(),
                    lessonName = settings["lesson"].orEmpty(),
                    principalPhone = settings["phone"].orEmpty(),
                    themeMode = settings["theme"] ?: "system",
                    dynamicColorEnabled = settings["dynamic"] != "false",
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
        showMessage(if (next) "رنگ پویا (Dynamic Color) فعال شد" else "تم استاندارد Material Expressive فعال شد")
    }

    fun updateTeacherName(value: String) {
        _uiState.update { it.copy(teacherName = value) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("teacher_name", value) }
    }

    fun updateLessonName(value: String) {
        _uiState.update { it.copy(lessonName = value) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("lesson_name", value) }
    }

    fun updatePrincipalPhone(value: String) {
        _uiState.update { it.copy(principalPhone = value) }
        viewModelScope.launch(Dispatchers.IO) { engine.setSetting("principal_phone", value) }
    }

    fun updateClassTime(value: String) {
        _uiState.update { it.copy(classTime = value) }
    }

    fun switchTab(tabIndex: Int) {
        _uiState.update { it.copy(activeTab = tabIndex) }
        if (tabIndex == 1) loadAnalyticsAndMonthly()
    }

    fun refreshClassesAndData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val allClasses = withContext(Dispatchers.IO) { engine.getClasses() }
            resolveCategorySelection(
                allClasses = allClasses,
                wantedSchool = _uiState.value.selectedSchool,
                wantedMajor = _uiState.value.selectedMajor,
                wantedGrade = _uiState.value.selectedGrade,
                wantedSection = _uiState.value.selectedSection
            )
            loadAttendanceSnapshot()
            if (_uiState.value.activeTab == 1) loadAnalyticsAndMonthly()
        }
    }

    fun selectSchool(school: String) {
        resolveCategorySelection(_uiState.value.classes, school, "", "", 1)
        loadAttendanceSnapshot()
        if (_uiState.value.activeTab == 1) loadAnalyticsAndMonthly()
    }

    fun selectMajor(major: String) {
        val st = _uiState.value
        resolveCategorySelection(st.classes, st.selectedSchool, major, st.selectedGrade, st.selectedSection)
        loadAttendanceSnapshot()
        if (st.activeTab == 1) loadAnalyticsAndMonthly()
    }

    fun selectGrade(grade: String) {
        val st = _uiState.value
        resolveCategorySelection(st.classes, st.selectedSchool, st.selectedMajor, grade, st.selectedSection)
        loadAttendanceSnapshot()
        if (st.activeTab == 1) loadAnalyticsAndMonthly()
    }

    fun selectSection(section: Int) {
        val st = _uiState.value
        resolveCategorySelection(st.classes, st.selectedSchool, st.selectedMajor, st.selectedGrade, section)
        loadAttendanceSnapshot()
        if (st.activeTab == 1) loadAnalyticsAndMonthly()
    }

    private fun resolveCategorySelection(
        allClasses: List<ClassGroup>,
        wantedSchool: String,
        wantedMajor: String,
        wantedGrade: String,
        wantedSection: Int
    ) {
        if (allClasses.isEmpty()) {
            _uiState.update {
                it.copy(
                    classes = emptyList(),
                    schools = emptyList(),
                    selectedSchool = "",
                    majorsForSchool = emptyList(),
                    selectedMajor = "",
                    gradesForSelection = emptyList(),
                    selectedGrade = "",
                    sectionsForSelection = emptyList(),
                    selectedSection = 1,
                    selectedClass = null,
                    jalaliDate = engine.formatJalaliDate(it.selectedDate.toString())
                )
            }
            return
        }

        val schools = allClasses.map { it.schoolName }.distinct()
        val school = if (wantedSchool in schools) wantedSchool else schools.first()
        val inSchool = allClasses.filter { it.schoolName == school }

        val majors = inSchool.map { it.major }.filter { it.isNotBlank() }.distinct()
        val major = when {
            majors.isEmpty() -> ""
            wantedMajor in majors -> wantedMajor
            else -> majors.first()
        }
        val inMajor = if (majors.isEmpty()) inSchool else inSchool.filter { it.major == major }

        val grades = inMajor.map { it.grade }.distinct()
        val grade = if (wantedGrade in grades) wantedGrade else grades.first()
        val inGrade = inMajor.filter { it.grade == grade }

        val sections = inGrade.map { it.section }.distinct().sorted()
        val section = if (wantedSection in sections) wantedSection else sections.first()
        val selectedClass = inGrade.find { it.section == section } ?: inGrade.firstOrNull()

        _uiState.update {
            it.copy(
                classes = allClasses,
                schools = schools,
                selectedSchool = school,
                majorsForSchool = majors,
                selectedMajor = major,
                gradesForSelection = grades,
                selectedGrade = grade,
                sectionsForSelection = sections,
                selectedSection = section,
                selectedClass = selectedClass
            )
        }
    }

    fun selectPeriod(period: Period) {
        val defaultTime = when (period) {
            Period.FIRST -> "08:00"
            Period.SECOND -> "09:00"
            Period.THIRD -> "10:00"
            Period.FOURTH -> "11:00"
        }
        _uiState.update { it.copy(selectedPeriod = period, classTime = defaultTime) }
        loadAttendanceSnapshot()
    }

    fun selectDateIso(dateIso: String) {
        runCatching { LocalDate.parse(dateIso) }.onSuccess { date ->
            _uiState.update { it.copy(selectedDate = date) }
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

    fun toggleMonthlySort() {
        _uiState.update { it.copy(sortMonthlyByAbsence = !it.sortMonthlyByAbsence) }
    }

    fun updateSearch(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
        loadAttendanceSnapshot()
    }

    fun setStudentStatus(studentId: Long, status: AttendanceStatus) {
        val st = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setAttendance(
                    studentId = studentId,
                    dateIso = st.selectedDate.toString(),
                    period = st.selectedPeriod,
                    status = status,
                    note = "",
                    teacherName = st.teacherName,
                    lessonName = st.lessonName,
                    classTime = st.classTime
                )
            }
            loadAttendanceSnapshot()
        }
    }

    /** دکمه دوتا تیک: کل دانش‌آموزان کلاس را (حتی غایب‌ها و تأخیری‌ها) دوباره به «حاضر» برمی‌گرداند */
    fun resetAllToPresent() {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val count = withContext(Dispatchers.IO) {
                engine.markClassStatus(
                    schoolName = cls.schoolName,
                    major = cls.major,
                    grade = cls.grade,
                    section = cls.section,
                    dateIso = st.selectedDate.toString(),
                    period = st.selectedPeriod,
                    status = AttendanceStatus.PRESENT,
                    onlyUnmarked = false,
                    teacherName = st.teacherName,
                    lessonName = st.lessonName,
                    classTime = st.classTime
                )
            }
            loadAttendanceSnapshot()
            showMessage("همه $count دانش‌آموز به حالت حاضر درآمدند و ثبت شدند")
        }
    }

    fun copyFromPreviousPeriod() {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        if (st.selectedPeriod == Period.FIRST) {
            showMessage("زنگ اول، زنگ قبلی ندارد")
            return
        }
        viewModelScope.launch {
            val copied = withContext(Dispatchers.IO) {
                engine.copyFromPreviousPeriod(
                    cls.schoolName, cls.major, cls.grade, cls.section,
                    st.selectedDate.toString(), st.selectedPeriod
                )
            }
            loadAttendanceSnapshot()
            showMessage(if (copied > 0) "حضور و غیاب $copied نفر از زنگ قبل کپی شد" else "در زنگ قبل موردی ثبت نشده است")
        }
    }

    fun addStudentToCurrentClass(first: String, last: String, father: String, nationalId: String, mobile: String) {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    engine.addStudent(cls.schoolName, cls.major, cls.grade, cls.section, first, last, father, nationalId, mobile)
                }
                refreshClassesAndData()
                showMessage("دانش‌آموز به کلاس اضافه شد")
            } catch (e: Exception) {
                showMessage(e.message ?: "خطا در افزودن دانش‌آموز")
            }
        }
    }

    fun updateStudent(studentId: Long, first: String, last: String, father: String, nationalId: String, mobile: String) {
        viewModelScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    engine.updateStudent(studentId, first, last, father, nationalId, mobile)
                }
                loadAttendanceSnapshot()
                showMessage("اطلاعات دانش‌آموز به‌روزرسانی شد")
            } catch (e: Exception) {
                showMessage(e.message ?: "خطا در ویرایش دانش‌آموز")
            }
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
            val count = withContext(Dispatchers.IO) {
                engine.deleteClass(cls.schoolName, cls.major, cls.grade, cls.section)
            }
            refreshClassesAndData()
            showMessage("کلاس و $count دانش‌آموز آن حذف شدند")
        }
    }

    fun importFileBytes(fileName: String, bytes: ByteArray, replaceExisting: Boolean = false) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val report = withContext(Dispatchers.IO) { engine.importFileBytes(fileName, bytes, replaceExisting) }
                refreshClassesAndData()
                showMessage("${report.importedCount} دانش‌آموز در ${report.classesCount} کلاس وارد شد")
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
                showMessage("پشتیبان بازیابی شد: ${rep.importedCount} دانش‌آموز در ${rep.classesCount} کلاس")
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
            onReady("hozoor_backup_${st.selectedDate}.json", json.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportTemplateExcel(onReady: (String, ByteArray) -> Unit) {
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) { engine.exportTemplateXlsx() }
            onReady("نمونه_ورود_دانش_آموزان.xlsx", bytes)
        }
    }

    fun generatePeriodGroupMessage(targetStatus: AttendanceStatus, onReady: (String) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            try {
                val msg = withContext(Dispatchers.IO) {
                    engine.generatePeriodGroupMessage(
                        cls.schoolName, cls.major, cls.grade, cls.section,
                        st.selectedDate.toString(), st.selectedPeriod, targetStatus,
                        st.teacherName, st.lessonName
                    )
                }
                onReady(msg)
            } catch (e: Exception) {
                showMessage(e.message ?: "موردی یافت نشد")
            }
        }
    }

    fun preparePrincipalReport(wholeSchool: Boolean = _uiState.value.reportWholeSchool) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        _uiState.update { it.copy(reportWholeSchool = wholeSchool) }
        viewModelScope.launch {
            val bundle = withContext(Dispatchers.IO) {
                engine.generatePrincipalReport(
                    cls.schoolName, cls.major, cls.grade, cls.section,
                    st.selectedDate.toString(), wholeSchool, st.teacherName
                )
            }
            _uiState.update { it.copy(principalReport = bundle) }
        }
    }

    fun exportDailyExcel(wholeSchool: Boolean, onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) {
                engine.exportDailyXlsx(cls.schoolName, cls.major, cls.grade, cls.section, st.selectedDate.toString(), wholeSchool)
            }
            val prefix = if (wholeSchool) "hozoor_school" else "hozoor_${cls.grade}_${cls.section}"
            onReady("${prefix}_${st.selectedDate}.xlsx", bytes)
        }
    }

    fun exportCurrentClassCsv(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) {
                engine.exportDailyCsv(cls.schoolName, cls.major, cls.grade, cls.section, st.selectedDate.toString())
            }
            onReady("hozoor_${cls.grade}_${cls.section}_${st.selectedDate}.csv", csv.toByteArray(Charsets.UTF_8))
        }
    }

    fun exportMonthlyExcel(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val bytes = withContext(Dispatchers.IO) {
                engine.exportMonthlyXlsx(cls.schoolName, cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth)
            }
            onReady("monthly_${cls.grade}_${cls.section}_${st.monthlyYear}_${st.monthlyMonth}.xlsx", bytes)
        }
    }

    fun exportMonthlyCsv(onReady: (String, ByteArray) -> Unit) {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val csv = withContext(Dispatchers.IO) {
                engine.exportMonthlyCsv(cls.schoolName, cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth)
            }
            onReady("monthly_${cls.grade}_${cls.section}_${st.monthlyYear}_${st.monthlyMonth}.csv", csv.toByteArray(Charsets.UTF_8))
        }
    }

    fun showMessage(msg: String) {
        _uiState.update { it.copy(snackbarMessage = msg) }
    }

    fun clearSnackbar() {
        _uiState.update { it.copy(snackbarMessage = null) }
    }

    private fun loadAnalyticsAndMonthly() {
        val st = _uiState.value
        val cls = st.selectedClass ?: return
        viewModelScope.launch {
            val (analytics, monthly) = withContext(Dispatchers.IO) {
                engine.getClassAnalytics(cls.schoolName, cls.major, cls.grade, cls.section) to
                    engine.getMonthlyReport(cls.schoolName, cls.major, cls.grade, cls.section, st.monthlyYear, st.monthlyMonth)
            }
            _uiState.update { it.copy(classAnalytics = analytics, monthlyReport = monthly) }
        }
    }

    private fun loadAttendanceSnapshot() {
        val st = _uiState.value
        val cls = st.selectedClass
        if (cls == null) {
            _uiState.update {
                it.copy(
                    isLoading = false,
                    students = emptyList(),
                    isPeriodSaved = false,
                    summary = PeriodSummary(0, 0, 0, 0, 0, 0),
                    jalaliDate = engine.formatJalaliDate(st.selectedDate.toString())
                )
            }
            return
        }
        viewModelScope.launch {
            val snap = withContext(Dispatchers.IO) {
                engine.getClassAttendance(
                    cls.schoolName, cls.major, cls.grade, cls.section,
                    st.selectedDate.toString(), st.selectedPeriod, st.searchQuery
                )
            }
            _uiState.update {
                it.copy(
                    isLoading = false,
                    jalaliDate = snap.jalaliDate,
                    isPeriodSaved = snap.isPeriodSaved,
                    summary = snap.summary,
                    students = snap.students
                )
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ClassCategorySelector.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

@Composable
fun ClassCategorySelector(
    schools: List<String>,
    selectedSchool: String,
    majors: List<String>,
    selectedMajor: String,
    grades: List<String>,
    selectedGrade: String,
    sections: List<Int>,
    selectedSection: Int,
    onSelectSchool: (String) -> Unit,
    onSelectMajor: (String) -> Unit,
    onSelectGrade: (String) -> Unit,
    onSelectSection: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp),
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
    ) {
        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            if (schools.size > 1) {
                CategoryGridRow(
                    title = "مدرسه",
                    items = schools,
                    selected = selectedSchool,
                    labelOf = { it },
                    selectedBg = MaterialTheme.colorScheme.primary,
                    selectedFg = MaterialTheme.colorScheme.onPrimary,
                    unselectedBg = MaterialTheme.colorScheme.surfaceContainerHigh,
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectSchool
                )
            }
            if (majors.isNotEmpty()) {
                CategoryGridRow(
                    title = "رشته",
                    items = majors,
                    selected = selectedMajor,
                    labelOf = { it },
                    selectedBg = MaterialTheme.colorScheme.primary,
                    selectedFg = MaterialTheme.colorScheme.onPrimary,
                    unselectedBg = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.45f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectMajor
                )
            }
            if (grades.isNotEmpty()) {
                CategoryGridRow(
                    title = "پایه",
                    items = grades,
                    selected = selectedGrade,
                    labelOf = { it },
                    selectedBg = MaterialTheme.colorScheme.secondary,
                    selectedFg = MaterialTheme.colorScheme.onSecondary,
                    unselectedBg = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.55f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectGrade
                )
            }
            if (sections.size > 1) {
                CategoryGridRow(
                    title = "شعبه",
                    items = sections,
                    selected = selectedSection,
                    labelOf = { "شعبه ${toPersianDigits(it.toString())}" },
                    selectedBg = MaterialTheme.colorScheme.tertiary,
                    selectedFg = MaterialTheme.colorScheme.onTertiary,
                    unselectedBg = MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.55f),
                    unselectedFg = MaterialTheme.colorScheme.onSurface,
                    onSelect = onSelectSection
                )
            }
        }
    }
}

@Composable
private fun <T> CategoryGridRow(
    title: String,
    items: List<T>,
    selected: T,
    labelOf: (T) -> String,
    selectedBg: Color,
    selectedFg: Color,
    unselectedBg: Color,
    unselectedFg: Color,
    onSelect: (T) -> Unit
) {
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 4.dp, start = 2.dp)
        )
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            items.chunked(3).forEach { chunk ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    chunk.forEach { item ->
                        val isSelected = item == selected
                        Surface(
                            onClick = { onSelect(item) },
                            shape = RoundedCornerShape(14.dp),
                            color = if (isSelected) selectedBg else unselectedBg,
                            border = if (isSelected) BorderStroke(2.dp, MaterialTheme.colorScheme.outline) else null,
                            modifier = Modifier.weight(1f).height(42.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.Center,
                                modifier = Modifier.padding(horizontal = 6.dp)
                            ) {
                                Text(
                                    text = labelOf(item),
                                    style = MaterialTheme.typography.labelLarge,
                                    fontWeight = if (isSelected) FontWeight.ExtraBold else FontWeight.SemiBold,
                                    color = if (isSelected) selectedFg else unselectedFg,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                    textAlign = TextAlign.Center
                                )
                            }
                        }
                    }
                    repeat(3 - chunk.size) { Spacer(Modifier.weight(1f)) }
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/PeriodSelector.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.NotificationsActive
import androidx.compose.material3.ButtonGroupDefaults
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.ToggleButton
import androidx.compose.material3.ToggleButtonDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import uniffi.hozoor_core.Period

private val ALL_PERIODS = listOf(
    Period.FIRST to "زنگ ۱",
    Period.SECOND to "زنگ ۲",
    Period.THIRD to "زنگ ۳",
    Period.FOURTH to "زنگ ۴"
)

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun PeriodSelector(
    selectedPeriod: Period,
    onSelectPeriod: (Period) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current

    Row(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(ButtonGroupDefaults.ConnectedSpaceBetween)
    ) {
        ALL_PERIODS.forEachIndexed { index, (period, label) ->
            val checked = selectedPeriod == period
            val shapes = when (index) {
                0 -> ButtonGroupDefaults.connectedLeadingButtonShapes()
                ALL_PERIODS.lastIndex -> ButtonGroupDefaults.connectedTrailingButtonShapes()
                else -> ButtonGroupDefaults.connectedMiddleButtonShapes()
            }

            ToggleButton(
                checked = checked,
                onCheckedChange = {
                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                    onSelectPeriod(period)
                },
                modifier = Modifier.weight(1f),
                shapes = shapes,
                colors = ToggleButtonDefaults.toggleButtonColors(
                    checkedContainerColor = MaterialTheme.colorScheme.primary,
                    checkedContentColor = MaterialTheme.colorScheme.onPrimary,
                    containerColor = MaterialTheme.colorScheme.surfaceContainerHigh,
                    contentColor = MaterialTheme.colorScheme.onSurface
                )
            ) {
                if (checked) {
                    Icon(Icons.Rounded.NotificationsActive, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                }
                Text(
                    text = label,
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = if (checked) FontWeight.ExtraBold else FontWeight.Medium,
                    maxLines = 1
                )
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/StudentAttendanceCard.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Call
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Delete
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.VerifiedUser
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.StudentAttendanceRow

@Composable
fun StudentAttendanceCard(
    indexInClass: Int,
    student: StudentAttendanceRow,
    onStatusChange: (AttendanceStatus) -> Unit,
    onSendIndividualNotice: (StudentAttendanceRow, AttendanceStatus) -> Unit,
    onCallParent: (String) -> Unit,
    onEditStudent: (StudentAttendanceRow) -> Unit,
    onDeleteStudent: (StudentAttendanceRow) -> Unit,
    modifier: Modifier = Modifier
) {
    val haptic = LocalHapticFeedback.current
    val accentColor = statusPrimaryColor(student.currentStatus)

    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 5.dp),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow,
        border = BorderStroke(1.2.dp, accentColor.copy(alpha = 0.55f)),
        tonalElevation = 1.dp
    ) {
        Row(modifier = Modifier.fillMaxWidth().height(IntrinsicSize.Min)) {
            Box(modifier = Modifier.width(6.dp).fillMaxHeight().background(accentColor))

            Column(modifier = Modifier.weight(1f).padding(12.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(RoundedCornerShape(11.dp))
                            .background(MaterialTheme.colorScheme.primaryContainer),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = toPersianDigits(indexInClass.toString()),
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }

                    Spacer(Modifier.width(10.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "${student.firstName} ${student.lastName}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.onSurface,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                        val meta = buildString {
                            if (student.fatherName.isNotBlank()) append("فرزند ${student.fatherName}")
                            if (student.mobile.isNotBlank()) {
                                if (isNotEmpty()) append(" · ")
                                append(toPersianDigits(student.mobile))
                            }
                        }
                        if (meta.isNotBlank()) {
                            Text(
                                text = meta,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        student.periodStatuses.forEachIndexed { i, st ->
                            val dotBg = if (st == AttendanceStatus.UNMARKED) {
                                MaterialTheme.colorScheme.surfaceContainerHighest
                            } else statusPrimaryColor(st)
                            val dotFg = if (st == AttendanceStatus.UNMARKED) {
                                MaterialTheme.colorScheme.onSurfaceVariant
                            } else statusOnColor(st)
                            Box(
                                modifier = Modifier.size(22.dp).clip(CircleShape).background(dotBg),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = toPersianDigits((i + 1).toString()),
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = dotFg
                                )
                            }
                        }
                    }
                }

                Spacer(Modifier.height(10.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    StatusActionChip("حاضر", Icons.Rounded.Check, student.currentStatus == AttendanceStatus.PRESENT, StatusColors.Present, StatusColors.OnPresent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onStatusChange(AttendanceStatus.PRESENT)
                    }
                    StatusActionChip("غایب", Icons.Rounded.Close, student.currentStatus == AttendanceStatus.ABSENT, StatusColors.Absent, StatusColors.OnAbsent, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onStatusChange(AttendanceStatus.ABSENT)
                    }
                    StatusActionChip("تأخیر", Icons.Rounded.Schedule, student.currentStatus == AttendanceStatus.LATE, StatusColors.Late, StatusColors.OnLate, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onStatusChange(AttendanceStatus.LATE)
                    }
                    StatusActionChip("موجه", Icons.Rounded.VerifiedUser, student.currentStatus == AttendanceStatus.EXCUSED, StatusColors.Excused, StatusColors.OnExcused, Modifier.weight(1f)) {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        onStatusChange(AttendanceStatus.EXCUSED)
                    }
                }

                Spacer(Modifier.height(8.dp))

                val canSendAbsent = student.currentStatus == AttendanceStatus.ABSENT
                val canSendLate = student.currentStatus == AttendanceStatus.LATE
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CompactActionBtn(
                        label = if (canSendLate) "پیام تأخیر" else "پیام غیبت",
                        icon = Icons.Rounded.Sms,
                        enabled = canSendAbsent || canSendLate,
                        highlightBg = if (canSendLate) StatusColors.Late else StatusColors.Absent,
                        highlightFg = if (canSendLate) StatusColors.OnLate else StatusColors.OnAbsent,
                        modifier = Modifier.weight(1.4f),
                        onClick = {
                            if (canSendAbsent) onSendIndividualNotice(student, AttendanceStatus.ABSENT)
                            else if (canSendLate) onSendIndividualNotice(student, AttendanceStatus.LATE)
                        }
                    )
                    CompactActionBtn(
                        label = "تماس",
                        icon = Icons.Rounded.Call,
                        enabled = student.mobile.isNotBlank(),
                        highlightBg = MaterialTheme.colorScheme.secondaryContainer,
                        highlightFg = MaterialTheme.colorScheme.onSecondaryContainer,
                        modifier = Modifier.weight(1f),
                        onClick = { onCallParent(student.mobile) }
                    )
                    CompactActionBtn(
                        label = "ویرایش",
                        icon = Icons.Rounded.Edit,
                        enabled = true,
                        highlightBg = MaterialTheme.colorScheme.surfaceContainerHigh,
                        highlightFg = MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.weight(1f),
                        onClick = { onEditStudent(student) }
                    )
                    CompactActionBtn(
                        label = "حذف",
                        icon = Icons.Rounded.Delete,
                        enabled = true,
                        highlightBg = MaterialTheme.colorScheme.errorContainer,
                        highlightFg = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.weight(0.9f),
                        onClick = { onDeleteStudent(student) }
                    )
                }
            }
        }
    }
}

@Composable
private fun StatusActionChip(
    label: String,
    icon: ImageVector,
    selected: Boolean,
    activeBg: Color,
    activeFg: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg = if (selected) activeBg else MaterialTheme.colorScheme.surfaceContainerHigh
    val fg = if (selected) activeFg else MaterialTheme.colorScheme.onSurface
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(if (selected) 50 else 12))
            .background(bg)
            .clickable(onClick = onClick)
            .padding(vertical = 8.dp, horizontal = 3.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(14.dp))
        Spacer(Modifier.width(3.dp))
        Text(text = label, style = MaterialTheme.typography.labelMedium, fontWeight = if (selected) FontWeight.ExtraBold else FontWeight.SemiBold, color = fg, maxLines = 1)
    }
}

@Composable
private fun CompactActionBtn(
    label: String,
    icon: ImageVector,
    enabled: Boolean,
    highlightBg: Color,
    highlightFg: Color,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val bg = if (enabled) highlightBg else MaterialTheme.colorScheme.surfaceContainer
    val fg = if (enabled) highlightFg else MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.45f)
    Row(
        modifier = modifier
            .clip(RoundedCornerShape(10.dp))
            .background(bg)
            .clickable(enabled = enabled, onClick = onClick)
            .padding(vertical = 7.dp, horizontal = 4.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(icon, contentDescription = label, tint = fg, modifier = Modifier.size(14.dp))
        Spacer(Modifier.width(3.dp))
        Text(text = label, style = MaterialTheme.typography.labelSmall, fontWeight = FontWeight.Bold, color = fg, maxLines = 1)
    }
}

fun statusPrimaryColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.PRESENT -> StatusColors.Present
    AttendanceStatus.ABSENT -> StatusColors.Absent
    AttendanceStatus.LATE -> StatusColors.Late
    AttendanceStatus.EXCUSED -> StatusColors.Excused
    AttendanceStatus.UNMARKED -> StatusColors.Unmarked
}

fun statusOnColor(status: AttendanceStatus): Color = when (status) {
    AttendanceStatus.PRESENT -> StatusColors.OnPresent
    AttendanceStatus.ABSENT -> StatusColors.OnAbsent
    AttendanceStatus.LATE -> StatusColors.OnLate
    AttendanceStatus.EXCUSED -> StatusColors.OnExcused
    AttendanceStatus.UNMARKED -> Color.White
}

fun toPersianDigits(input: String): String {
    val fa = charArrayOf('۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹')
    return buildString(input.length) {
        for (c in input) if (c in '0'..'9') append(fa[c - '0']) else append(c)
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/JalaliDatePickerDialog.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.JalaliDayCell
import uniffi.hozoor_core.JalaliMonthGrid
import java.time.LocalDate

private val WEEK_HEADERS = listOf("ش", "ی", "د", "س", "چ", "پ", "ج")

@Composable
fun JalaliDatePickerDialog(
    initialYear: Int,
    initialMonth: Int,
    selectedIso: String,
    gridProvider: (year: Int, month: Int) -> JalaliMonthGrid,
    onSelectIso: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var year by remember { mutableIntStateOf(initialYear) }
    var month by remember { mutableIntStateOf(initialMonth) }
    val todayIso = remember { LocalDate.now().toString() }
    val grid = remember(year, month) { gridProvider(year, month) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(26.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, tonalElevation = 6.dp) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    IconButton(onClick = { if (month == 1) { month = 12; year -= 1 } else month -= 1 }) {
                        Icon(Icons.Rounded.ChevronRight, contentDescription = "ماه قبل")
                    }
                    Text(grid.monthLabel, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                    IconButton(onClick = { if (month == 12) { month = 1; year += 1 } else month += 1 }) {
                        Icon(Icons.Rounded.ChevronLeft, contentDescription = "ماه بعد")
                    }
                }

                Spacer(Modifier.height(8.dp))

                Row(modifier = Modifier.fillMaxWidth()) {
                    WEEK_HEADERS.forEachIndexed { idx, w ->
                        Text(
                            text = w,
                            modifier = Modifier.weight(1f),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.ExtraBold,
                            color = if (idx == 6) StatusColors.Absent else MaterialTheme.colorScheme.primary
                        )
                    }
                }

                Spacer(Modifier.height(6.dp))

                val cells: List<JalaliDayCell?> = List(grid.leadingBlanks) { null } + grid.days
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    cells.chunked(7).forEach { week ->
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            week.forEach { cell ->
                                if (cell == null) {
                                    Spacer(Modifier.weight(1f).aspectRatio(1f))
                                } else {
                                    val isSelected = cell.dateIso == selectedIso
                                    val isToday = cell.dateIso == todayIso
                                    val bg = when {
                                        isSelected -> MaterialTheme.colorScheme.primary
                                        cell.isFriday -> StatusColors.Absent.copy(alpha = 0.14f)
                                        else -> MaterialTheme.colorScheme.surface
                                    }
                                    val fg = when {
                                        isSelected -> MaterialTheme.colorScheme.onPrimary
                                        cell.isFriday -> StatusColors.Absent
                                        else -> MaterialTheme.colorScheme.onSurface
                                    }
                                    Surface(
                                        shape = RoundedCornerShape(10.dp),
                                        color = bg,
                                        border = if (isToday && !isSelected) BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null,
                                        modifier = Modifier
                                            .weight(1f)
                                            .aspectRatio(1f)
                                            .clip(RoundedCornerShape(10.dp))
                                            .clickable {
                                                onSelectIso(cell.dateIso)
                                                onDismiss()
                                            }
                                    ) {
                                        Box(contentAlignment = Alignment.Center) {
                                            Text(toPersianDigits(cell.day.toString()), style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold, color = fg)
                                        }
                                    }
                                }
                            }
                            repeat(7 - week.size) { Spacer(Modifier.weight(1f).aspectRatio(1f)) }
                        }
                    }
                }

                Spacer(Modifier.height(14.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("انصراف") }
                    Button(onClick = { onSelectIso(todayIso); onDismiss() }, modifier = Modifier.weight(1f)) { Text("امروز") }
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/StudentEditDialog.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import uniffi.hozoor_core.StudentAttendanceRow

@Composable
fun StudentEditDialog(
    editingStudent: StudentAttendanceRow?,
    onSave: (first: String, last: String, father: String, nationalId: String, mobile: String) -> Unit,
    onDismiss: () -> Unit
) {
    var first by remember { mutableStateOf(editingStudent?.firstName.orEmpty()) }
    var last by remember { mutableStateOf(editingStudent?.lastName.orEmpty()) }
    var father by remember { mutableStateOf(editingStudent?.fatherName.orEmpty()) }
    var nationalId by remember { mutableStateOf(editingStudent?.nationalId.orEmpty()) }
    var mobile by remember { mutableStateOf(editingStudent?.mobile.orEmpty()) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh) {
            Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = if (editingStudent == null) "افزودن دانش‌آموز جدید" else "ویرایش مشخصات دانش‌آموز",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.ExtraBold
                )
                OutlinedTextField(value = first, onValueChange = { first = it }, label = { Text("نام") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = last, onValueChange = { last = it }, label = { Text("نام خانوادگی") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = father, onValueChange = { father = it }, label = { Text("نام پدر") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = nationalId, onValueChange = { nationalId = it.take(10) }, label = { Text("کد ملی (۱۰ رقم)") }, singleLine = true, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = mobile, onValueChange = { mobile = it }, label = { Text("شماره موبایل") }, singleLine = true, modifier = Modifier.fillMaxWidth())

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = onDismiss, modifier = Modifier.weight(1f)) { Text("لغو") }
                    Button(
                        onClick = { onSave(first, last, father, nationalId, mobile); onDismiss() },
                        modifier = Modifier.weight(1f)
                    ) { Text("ذخیره") }
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExpressiveToolbar.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.DoneAll
import androidx.compose.material.icons.rounded.PersonAdd
import androidx.compose.material.icons.rounded.Share
import androidx.compose.material.icons.rounded.UploadFile
import androidx.compose.material3.ExperimentalMaterial3ExpressiveApi
import androidx.compose.material3.FloatingToolbarDefaults
import androidx.compose.material3.HorizontalFloatingToolbar
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import uniffi.hozoor_core.Period

@OptIn(ExperimentalMaterial3ExpressiveApi::class)
@Composable
fun ExpressiveAttendanceToolbar(
    selectedPeriod: Period,
    onResetAllPresent: () -> Unit,
    onCopyFromPrevious: () -> Unit,
    onAddStudent: () -> Unit,
    onOpenExportSheet: () -> Unit,
    onImportFile: () -> Unit,
    modifier: Modifier = Modifier
) {
    HorizontalFloatingToolbar(
        expanded = true,
        modifier = modifier,
        colors = FloatingToolbarDefaults.vibrantFloatingToolbarColors(),
        floatingActionButton = {
            FloatingToolbarDefaults.VibrantFloatingActionButton(onClick = onImportFile) {
                Icon(Icons.Rounded.UploadFile, contentDescription = "ورود اکسل یا CSV")
            }
        }
    ) {
        IconButton(onClick = onResetAllPresent) {
            Icon(Icons.Rounded.DoneAll, contentDescription = "همه حاضر")
        }
        IconButton(onClick = onCopyFromPrevious, enabled = selectedPeriod != Period.FIRST) {
            Icon(Icons.Rounded.ContentCopy, contentDescription = "کپی از زنگ قبل")
        }
        IconButton(onClick = onAddStudent) {
            Icon(Icons.Rounded.PersonAdd, contentDescription = "افزودن دانش‌آموز")
        }
        IconButton(onClick = onOpenExportSheet) {
            Icon(Icons.Rounded.Share, contentDescription = "گزارش مدیر، خروجی و پشتیبان")
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/components/ExportAndReportSheet.kt": r'''package ir.hozoor.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Backup
import androidx.compose.material.icons.rounded.ContentCopy
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Download
import androidx.compose.material.icons.rounded.Phone
import androidx.compose.material.icons.rounded.Restore
import androidx.compose.material.icons.rounded.Send
import androidx.compose.material.icons.rounded.Sms
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import uniffi.hozoor_core.AttendanceStatus
import uniffi.hozoor_core.PrincipalReportBundle

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportAndReportSheet(
    report: PrincipalReportBundle?,
    wholeSchool: Boolean,
    principalPhone: String,
    onToggleWholeSchool: (Boolean) -> Unit,
    onPrincipalPhoneChange: (String) -> Unit,
    onSendSms: (phone: String, smsText: String) -> Unit,
    onShareText: (String) -> Unit,
    onCopyText: (String) -> Unit,
    onSendGroupPeriodSms: (AttendanceStatus) -> Unit,
    onSendGroupPeriodShare: (AttendanceStatus) -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onExportTemplateExcel: () -> Unit,
    onExportBackupJson: () -> Unit,
    onRestoreBackupJson: () -> Unit,
    onDismiss: () -> Unit
) {
    var previewSmsMode by remember { mutableStateOf(false) }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Text("گزارش مدیر، خروجی و پشتیبان‌گیری", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)

            OutlinedTextField(
                value = principalPhone,
                onValueChange = onPrincipalPhoneChange,
                label = { Text("شماره موبایل مدیر (برای پیامک عادی)") },
                placeholder = { Text("0917xxxxxxx") },
                leadingIcon = { Icon(Icons.Rounded.Phone, contentDescription = null) },
                singleLine = true,
                shape = RoundedCornerShape(16.dp),
                modifier = Modifier.fillMaxWidth()
            )

            Text("ارسال پیام گروهی همین زنگ به مدیر", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = { onSendGroupPeriodSms(AttendanceStatus.ABSENT) }, modifier = Modifier.weight(1f)) {
                    Text("غیبت با پیامک")
                }
                FilledTonalButton(onClick = { onSendGroupPeriodShare(AttendanceStatus.ABSENT) }, modifier = Modifier.weight(1f)) {
                    Text("غیبت در پیام‌رسان")
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { onSendGroupPeriodSms(AttendanceStatus.LATE) }, modifier = Modifier.weight(1f)) {
                    Text("تأخیر با پیامک")
                }
                OutlinedButton(onClick = { onSendGroupPeriodShare(AttendanceStatus.LATE) }, modifier = Modifier.weight(1f)) {
                    Text("تأخیر در پیام‌رسان")
                }
            }

            HorizontalDivider()

            Text("گزارش تجمیعی کل روز (بدون تکرار کل روز در زنگ‌ها)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = !wholeSchool, onClick = { onToggleWholeSchool(false) }, label = { Text("کلاس فعلی") })
                FilterChip(selected = wholeSchool, onClick = { onToggleWholeSchool(true) }, label = { Text("کل مدرسه") })
                Spacer(Modifier.weight(1f))
                FilterChip(
                    selected = previewSmsMode,
                    onClick = { previewSmsMode = !previewSmsMode },
                    label = { Text(if (previewSmsMode) "پیامک فشرده" else "متن کامل") }
                )
            }

            val previewText = when {
                report == null -> "در حال آماده‌سازی..."
                previewSmsMode -> report.smsText
                else -> report.fullText
            }

            Surface(shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, modifier = Modifier.fillMaxWidth()) {
                Text(previewText, style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(14.dp))
            }

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { report?.let { onSendSms(principalPhone, it.smsText) } }, enabled = report != null, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Sms, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("پیامک عادی")
                }
                FilledTonalButton(onClick = { report?.let { onShareText(it.fullText) } }, enabled = report != null, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Send, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("ارسال متن")
                }
                OutlinedButton(onClick = { onCopyText(previewText) }, enabled = report != null) {
                    Icon(Icons.Rounded.ContentCopy, contentDescription = "کپی")
                }
            }

            HorizontalDivider()

            Text("خروجی اکسل، CSV و فایل نمونه", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.TableChart, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("اکسل (.xlsx)")
                }
                OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Description, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("فایل CSV")
                }
            }
            OutlinedButton(onClick = onExportTemplateExcel, modifier = Modifier.fillMaxWidth()) {
                Icon(Icons.Rounded.Download, contentDescription = null)
                Spacer(Modifier.width(6.dp))
                Text("دریافت فایل نمونه Excel (XLSX)")
            }

            HorizontalDivider()

            Text("پشتیبان‌گیری و بازیابی کامل (JSON)", style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilledTonalButton(onClick = onExportBackupJson, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Backup, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("دانلود پشتیبان")
                }
                OutlinedButton(onClick = onRestoreBackupJson, modifier = Modifier.weight(1f)) {
                    Icon(Icons.Rounded.Restore, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("بازیابی JSON")
                }
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/MonthlyReportScreen.kt": r'''package ir.hozoor.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.ChevronLeft
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.DeleteSweep
import androidx.compose.material.icons.rounded.Description
import androidx.compose.material.icons.rounded.Sort
import androidx.compose.material.icons.rounded.TableChart
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import ir.hozoor.app.ui.components.toPersianDigits
import ir.hozoor.app.ui.theme.StatusColors
import uniffi.hozoor_core.ClassAnalytics
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.MonthlyStudentStat
import uniffi.hozoor_core.TopStudentCount
import java.util.Locale

@Composable
fun MonthlyReportContent(
    analytics: ClassAnalytics?,
    report: MonthlyClassReport?,
    sortByAbsence: Boolean,
    onShiftMonth: (Int) -> Unit,
    onToggleSort: () -> Unit,
    onExportExcel: () -> Unit,
    onExportCsv: () -> Unit,
    onRequestDeleteClass: () -> Unit,
    modifier: Modifier = Modifier
) {
    val students = remember(report, sortByAbsence) {
        val list = report?.students.orEmpty()
        if (sortByAbsence) list.sortedByDescending { it.absentPeriods } else list
    }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(bottom = 32.dp, top = 4.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // بخش ۱: آمار کلی کلاس + بیشترین غیبت، تأخیر و غیبت موجه (مطابق index.html)
        if (analytics != null) {
            item(key = "class_analytics") {
                Surface(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                    shape = RoundedCornerShape(22.dp),
                    color = MaterialTheme.colorScheme.surfaceContainerLow
                ) {
                    Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text("آمار کلی جلسات این کلاس", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold)
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            MonthlyKpi("دانش‌آموز", toPersianDigits(analytics.studentCount.toString()), MaterialTheme.colorScheme.primary)
                            MonthlyKpi("جلسه", toPersianDigits(analytics.recordedSessions.toString()), MaterialTheme.colorScheme.secondary)
                            MonthlyKpi("غایب", toPersianDigits(analytics.totalAbsent.toString()), StatusColors.Absent)
                            MonthlyKpi("تأخیر", toPersianDigits(analytics.totalLate.toString()), StatusColors.Late)
                            MonthlyKpi("موجه", toPersianDigits(analytics.totalExcused.toString()), StatusColors.Excused)
                        }
                        HorizontalDivider()
                        TopRankingBox("بیشترین غیبت", analytics.topAbsent, StatusColors.Absent)
                        TopRankingBox("بیشترین تأخیر", analytics.topLate, StatusColors.Late)
                        TopRankingBox("بیشترین غیبت موجه", analytics.topExcused, StatusColors.Excused)
                    }
                }
            }
        }

        // بخش ۲: انتخابگر ماه شمسی و خروجی ماهانه
        item(key = "monthly_header") {
            Surface(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                shape = RoundedCornerShape(22.dp),
                color = MaterialTheme.colorScheme.surfaceContainerHigh
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        IconButton(onClick = { onShiftMonth(-1) }) {
                            Icon(Icons.Rounded.ChevronRight, contentDescription = "ماه قبل")
                        }
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(report?.monthLabel ?: "—", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold)
                            Text(
                                text = "روزهای ثبت‌شده: ${toPersianDigits((report?.recordedDays ?: 0).toString())} روز",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        IconButton(onClick = { onShiftMonth(1) }) {
                            Icon(Icons.Rounded.ChevronLeft, contentDescription = "ماه بعد")
                        }
                    }

                    Spacer(Modifier.height(10.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceAround) {
                        MonthlyKpi("میانگین حضور", "${toPersianDigits(String.format(Locale.US, "%.1f", report?.averageAttendancePercent ?: 100.0))}٪", StatusColors.Present)
                        MonthlyKpi("غیبت کل روز", toPersianDigits((report?.totalFullAbsentDays ?: 0).toString()), StatusColors.Absent)
                        MonthlyKpi("زنگ غیبت", toPersianDigits((report?.totalAbsentPeriods ?: 0).toString()), StatusColors.Late)
                    }

                    Spacer(Modifier.height(12.dp))

                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        FilledTonalButton(onClick = onExportExcel, modifier = Modifier.weight(1f)) {
                            Icon(Icons.Rounded.TableChart, contentDescription = null)
                            Spacer(Modifier.width(4.dp))
                            Text("اکسل ماهانه")
                        }
                        OutlinedButton(onClick = onExportCsv, modifier = Modifier.weight(1f)) {
                            Icon(Icons.Rounded.Description, contentDescription = null)
                            Spacer(Modifier.width(4.dp))
                            Text("CSV ماهانه")
                        }
                        FilterChip(selected = sortByAbsence, onClick = onToggleSort, label = { Icon(Icons.Rounded.Sort, contentDescription = "مرتب‌سازی") })
                    }
                }
            }
        }

        itemsIndexed(items = students, key = { _, s -> s.studentId }) { idx, stat ->
            MonthlyStudentCard(index = idx + 1, stat = stat)
        }

        // دکمه امن حذف کل این کلاس
        item(key = "delete_class_footer") {
            OutlinedButton(
                onClick = onRequestDeleteClass,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error),
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                Icon(Icons.Rounded.DeleteSweep, contentDescription = null)
                Spacer(Modifier.width(6.dp))
                Text("حذف کامل این کلاس و سوابقش")
            }
        }
    }
}

@Composable
private fun TopRankingBox(title: String, items: List<TopStudentCount>, accent: Color) {
    Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
        Text(title, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.ExtraBold, color = accent)
        if (items.isEmpty()) {
            Text("موردی ثبت نشده است.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        } else {
            items.forEachIndexed { idx, row ->
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${toPersianDigits((idx + 1).toString())}. ${row.fullName}", style = MaterialTheme.typography.bodyMedium)
                    Text("${toPersianDigits(row.count.toString())} مورد", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = accent)
                }
            }
        }
    }
}

@Composable
private fun MonthlyKpi(title: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = color)
        Text(title, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun MonthlyStudentCard(index: Int, stat: MonthlyStudentStat) {
    val pct = (stat.attendancePercent / 100.0).toFloat().coerceIn(0f, 1f)
    val barColor = when {
        stat.attendancePercent >= 90.0 -> StatusColors.Present
        stat.attendancePercent >= 75.0 -> StatusColors.Late
        else -> StatusColors.Absent
    }
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surfaceContainerLow
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = "${toPersianDigits(index.toString())}. ${stat.firstName} ${stat.lastName}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                Text(
                    text = "${toPersianDigits(String.format(Locale.US, "%.1f", stat.attendancePercent))}٪",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.ExtraBold,
                    color = barColor
                )
            }
            Spacer(Modifier.height(6.dp))
            LinearProgressIndicator(progress = { pct }, color = barColor, modifier = Modifier.fillMaxWidth().height(6.dp))
            Spacer(Modifier.height(8.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("حاضر: ${toPersianDigits(stat.presentPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Present)
                Text("غایب: ${toPersianDigits(stat.absentPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Absent)
                Text("کل روز: ${toPersianDigits(stat.fullAbsentDays.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Absent)
                Text("تأخیر: ${toPersianDigits(stat.latePeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Late)
                Text("موجه: ${toPersianDigits(stat.excusedPeriods.toString())}", style = MaterialTheme.typography.labelMedium, color = StatusColors.Excused)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/ui/screens/AttendanceScreen.kt": r'''package ir.hozoor.app.ui.screens

import android.content.Intent
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
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
    var deletingStudent by remember { mutableStateOf<StudentAttendanceRow?>(null) }
    var showDeleteClassDialog by remember { mutableStateOf(false) }

    val filePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        uri ?: return@rememberLauncherForActivityResult
        val name = FileShareHelper.resolveFileName(context, uri)
        context.contentResolver.openInputStream(uri)?.use { stream ->
            viewModel.importFileBytes(fileName = name, bytes = stream.readBytes(), replaceExisting = false)
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

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        Box(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            Column(modifier = Modifier.fillMaxSize()) {
                // هدر عمومی + نام مدرسه فعال + تغییر تم (تاریک/روشن) و رنگ پویا (Dynamic Color)
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = state.selectedSchool.ifBlank { "سامانه حضور و غیاب" },
                            style = MaterialTheme.typography.headlineSmall,
                            fontWeight = FontWeight.ExtraBold,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(
                                text = state.jalaliDate,
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.Bold
                            )
                            if (state.classes.isNotEmpty() && state.activeTab == 0) {
                                Text(
                                    text = if (state.isPeriodSaved) "• ثبت‌شده" else "• پیش‌فرض حاضر",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = if (state.isPeriodSaved) StatusColors.Present else MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }

                    // دکمه رنگ پویا (Dynamic Color در اندروید ۱۲ به بالا)
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                        FilledTonalIconButton(onClick = viewModel::toggleDynamicColor) {
                            Icon(
                                imageVector = Icons.Rounded.Palette,
                                contentDescription = "رنگ پویا (Dynamic Color)",
                                tint = if (state.dynamicColorEnabled) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                        Spacer(Modifier.width(4.dp))
                    }

                    // دکمه تغییر حالت تاریک / روشن
                    FilledTonalIconButton(onClick = { viewModel.toggleDarkMode(isDarkTheme) }) {
                        Icon(
                            imageVector = if (isDarkTheme) Icons.Rounded.LightMode else Icons.Rounded.DarkMode,
                            contentDescription = "تغییر حالت تاریک یا روشن"
                        )
                    }
                }

                // نوار سریع تاریخ شمسی + پنل مشخصات دبیر/درس
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    FilledTonalButton(
                        onClick = { showDatePicker = true },
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Rounded.CalendarMonth, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(Modifier.width(6.dp))
                        Text("تقویم شمسی", maxLines = 1)
                    }
                    IconButton(onClick = { viewModel.shiftDate(-1) }) {
                        Icon(Icons.Rounded.ChevronRight, contentDescription = "روز قبل")
                    }
                    IconButton(onClick = { viewModel.shiftDate(1) }) {
                        Icon(Icons.Rounded.ChevronLeft, contentDescription = "روز بعد")
                    }
                    OutlinedButton(
                        onClick = { showTeacherPanel = !showTeacherPanel },
                        contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                    ) {
                        Text("دبیر و درس")
                        Icon(if (showTeacherPanel) Icons.Rounded.ExpandLess else Icons.Rounded.ExpandMore, contentDescription = null)
                    }
                }

                // پنل بازشو مشخصات دبیر، درس، شماره مدیر و ساعت کلاس
                AnimatedVisibility(visible = showTeacherPanel) {
                    Surface(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
                        shape = RoundedCornerShape(18.dp),
                        color = MaterialTheme.colorScheme.surfaceContainerLow
                    ) {
                        Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(
                                    value = state.teacherName,
                                    onValueChange = viewModel::updateTeacherName,
                                    label = { Text("نام دبیر") },
                                    singleLine = true,
                                    modifier = Modifier.weight(1f)
                                )
                                OutlinedTextField(
                                    value = state.lessonName,
                                    onValueChange = viewModel::updateLessonName,
                                    label = { Text("نام درس") },
                                    singleLine = true,
                                    modifier = Modifier.weight(1f)
                                )
                            }
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedTextField(
                                    value = state.principalPhone,
                                    onValueChange = viewModel::updatePrincipalPhone,
                                    label = { Text("موبایل مدیر") },
                                    singleLine = true,
                                    modifier = Modifier.weight(1.4f)
                                )
                                OutlinedTextField(
                                    value = state.classTime,
                                    onValueChange = viewModel::updateClassTime,
                                    label = { Text("ساعت") },
                                    singleLine = true,
                                    modifier = Modifier.weight(0.8f)
                                )
                            }
                        }
                    }
                }

                // تب‌های حضور روزانه و آمار/گزارش ماهانه
                if (state.classes.isNotEmpty()) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 2.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        FilterChip(selected = state.activeTab == 0, onClick = { viewModel.switchTab(0) }, label = { Text("حضور و غیاب روزانه") }, modifier = Modifier.weight(1f))
                        FilterChip(selected = state.activeTab == 1, onClick = { viewModel.switchTab(1) }, label = { Text("آمار و گزارش ماهانه") }, modifier = Modifier.weight(1f))
                    }
                }

                when {
                    state.isLoading -> {
                        Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { LoadingIndicator() }
                    }
                    state.classes.isEmpty() -> {
                        EmptyImportState(
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
                                    FileShareHelper.shareBytesAsFile(
                                        context, name,
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        bytes, "فایل نمونه Excel"
                                    )
                                }
                            }
                        )
                    }
                    state.activeTab == 1 -> {
                        ClassCategorySelector(
                            schools = state.schools,
                            selectedSchool = state.selectedSchool,
                            majors = state.majorsForSchool,
                            selectedMajor = state.selectedMajor,
                            grades = state.gradesForSelection,
                            selectedGrade = state.selectedGrade,
                            sections = state.sectionsForSelection,
                            selectedSection = state.selectedSection,
                            onSelectSchool = viewModel::selectSchool,
                            onSelectMajor = viewModel::selectMajor,
                            onSelectGrade = viewModel::selectGrade,
                            onSelectSection = viewModel::selectSection
                        )
                        MonthlyReportContent(
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
                    }
                    else -> {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(bottom = 104.dp, top = 2.dp)
                        ) {
                            // دسته‌بندی شبکه‌ای کلاس‌ها (اسکرول طبیعی با صفحه تا لیست دانش‌آموزان فضای کامل داشته باشد)
                            item(key = "category_grid") {
                                ClassCategorySelector(
                                    schools = state.schools,
                                    selectedSchool = state.selectedSchool,
                                    majors = state.majorsForSchool,
                                    selectedMajor = state.selectedMajor,
                                    grades = state.gradesForSelection,
                                    selectedGrade = state.selectedGrade,
                                    sections = state.sectionsForSelection,
                                    selectedSection = state.selectedSection,
                                    onSelectSchool = viewModel::selectSchool,
                                    onSelectMajor = viewModel::selectMajor,
                                    onSelectGrade = viewModel::selectGrade,
                                    onSelectSection = viewModel::selectSection
                                )
                            }

                            item(key = "period_selector") {
                                Spacer(Modifier.height(6.dp))
                                PeriodSelector(selectedPeriod = state.selectedPeriod, onSelectPeriod = viewModel::selectPeriod)
                                SummaryHeaderCard(summary = state.summary)
                                OutlinedTextField(
                                    value = state.searchQuery,
                                    onValueChange = viewModel::updateSearch,
                                    placeholder = { Text("جستجوی نام، نام خانوادگی، پدر یا کد ملی...") },
                                    leadingIcon = { Icon(Icons.Rounded.Search, contentDescription = null) },
                                    singleLine = true,
                                    shape = RoundedCornerShape(22.dp),
                                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 4.dp)
                                )
                            }

                            itemsIndexed(
                                items = state.students,
                                key = { _, s -> s.studentId },
                                contentType = { _, _ -> "student" }
                            ) { idx, student ->
                                StudentAttendanceCard(
                                    indexInClass = idx + 1,
                                    student = student,
                                    onStatusChange = { viewModel.setStudentStatus(student.studentId, it) },
                                    onCallParent = { phone ->
                                        context.startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone")))
                                    },
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
                                        val teacherDesc = if (state.teacherName.isNotBlank()) " با دبیر محترم ${state.teacherName}" else ""
                                        val body = "سلام علیکم، دانش‌آموز ${s.firstName} ${s.lastName}، فرزند ${s.fatherName.ifBlank { "ثبت نشده" }}، " +
                                            "$clsDesc، ${lessonDesc}مورخه ${state.jalaliDate} ($pTitle ساعت ${toPersianDigits(state.classTime)})$teacherDesc $statusText."
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

            if (state.activeTab == 0 && state.classes.isNotEmpty()) {
                ExpressiveAttendanceToolbar(
                    selectedPeriod = state.selectedPeriod,
                    onResetAllPresent = viewModel::resetAllToPresent,
                    onCopyFromPrevious = viewModel::copyFromPreviousPeriod,
                    onAddStudent = { showAddDialog = true },
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

    if (showDatePicker) {
        val ym = remember(state.selectedDate) { viewModel.currentDateJalaliYearMonth() }
        JalaliDatePickerDialog(
            initialYear = ym.year,
            initialMonth = ym.month,
            selectedIso = state.selectedDate.toString(),
            gridProvider = viewModel::getJalaliCalendarGrid,
            onSelectIso = viewModel::selectDateIso,
            onDismiss = { showDatePicker = false }
        )
    }

    if (showAddDialog) {
        StudentEditDialog(
            editingStudent = null,
            onSave = { f, l, fa, nid, mob -> viewModel.addStudentToCurrentClass(f, l, fa, nid, mob) },
            onDismiss = { showAddDialog = false }
        )
    }

    editingStudent?.let { st ->
        StudentEditDialog(
            editingStudent = st,
            onSave = { f, l, fa, nid, mob -> viewModel.updateStudent(st.studentId, f, l, fa, nid, mob) },
            onDismiss = { editingStudent = null }
        )
    }

    deletingStudent?.let { st ->
        AlertDialog(
            onDismissRequest = { deletingStudent = null },
            title = { Text("حذف دانش‌آموز") },
            text = { Text("آیا «${st.firstName} ${st.lastName}» و تمام سوابق حضور و غیاب او حذف شوند؟") },
            confirmButton = {
                TextButton(onClick = { viewModel.deleteStudent(st.studentId); deletingStudent = null }) {
                    Text("حذف", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = { TextButton(onClick = { deletingStudent = null }) { Text("انصراف") } }
        )
    }

    if (showDeleteClassDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteClassDialog = false },
            title = { Text("حذف کامل کلاس") },
            text = { Text("تمام دانش‌آموزان و سوابق کلاس انتخاب‌شده حذف می‌شوند. سایر کلاس‌ها دست‌نخورده می‌مانند. ادامه می‌دهید؟") },
            confirmButton = {
                TextButton(onClick = { viewModel.deleteCurrentClass(); showDeleteClassDialog = false }) {
                    Text("بله، حذف شود", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = { TextButton(onClick = { showDeleteClassDialog = false }) { Text("انصراف") } }
        )
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
            onSendGroupPeriodSms = { status ->
                viewModel.generatePeriodGroupMessage(status) { msg ->
                    FileShareHelper.openSmsApp(context, state.principalPhone, msg)
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
            onExportBackupJson = {
                viewModel.exportBackupJson { name, bytes ->
                    FileShareHelper.shareBytesAsFile(context, name, "application/json", bytes, "فایل پشتیبان JSON")
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
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surfaceContainer
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(vertical = 10.dp, horizontal = 12.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
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
    onDownloadTemplate: () -> Unit
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("سامانه حضور و غیاب آماده است", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.ExtraBold)
        Spacer(Modifier.height(8.dp))
        Text(
            text = "فایل اکسل (.xlsx) یا CSV مدرسه خود را انتخاب کنید تا کلاس‌ها به‌صورت خودکار بر اساس رشته، پایه و شعبه دسته‌بندی شوند.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(Modifier.height(20.dp))
        Button(onClick = onImportClick, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Rounded.UploadFile, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("انتخاب فایل اکسل یا CSV")
        }
        Spacer(Modifier.height(8.dp))
        FilledTonalButton(onClick = onLoadSampleClick, modifier = Modifier.fillMaxWidth()) {
            Text("تست سریع با داده‌های نمونه")
        }
        Spacer(Modifier.height(8.dp))
        OutlinedButton(onClick = onDownloadTemplate, modifier = Modifier.fillMaxWidth()) {
            Text("دریافت فایل نمونه Excel (XLSX)")
        }
    }
}
''',
}


def main():
    for rel_path, content in FILES.items():
        path = Path(rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Created: {rel_path}")
    print(f"\nPart 2 (Android Kotlin UI) done: {len(FILES)} files.")


if __name__ == "__main__":
    main()
