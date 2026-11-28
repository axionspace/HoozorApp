from pathlib import Path

FILES = {
    "android-app/settings.gradle.kts": r'''pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
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
        versionCode = 6
        versionName = "5.1.0"
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
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
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

    kotlinOptions { jvmTarget = "17" }
    buildFeatures { compose = true }
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
    <queries>
        <intent><action android:name="android.intent.action.SENDTO" /><data android:scheme="smsto" /></intent>
        <intent><action android:name="android.intent.action.VIEW" /><data android:scheme="sms" /></intent>
        <intent><action android:name="android.intent.action.VIEW" /><data android:scheme="https" /></intent>
        <intent><action android:name="android.intent.action.SEND" /><data android:mimeType="text/plain" /></intent>
        <intent><action android:name="android.intent.action.DIAL" /><data android:scheme="tel" /></intent>
        <intent><action android:name="android.intent.action.PICK" /><data android:mimeType="vnd.android.cursor.dir/phone_v2" /></intent>
        <intent><action android:name="android.intent.action.PICK" /><data android:mimeType="vnd.android.cursor.dir/contact" /></intent>
        <package android:name="com.google.android.contacts" />
        <package android:name="com.android.contacts" />
        <package android:name="com.samsung.android.app.contacts" />
        <package android:name="com.miui.contacts" />
        <package android:name="com.huawei.contacts" />
        <package android:name="com.hihonor.contacts" />
        <package android:name="com.oplus.contacts" />
    </queries>

    <application
        android:name=".HozoorApplication"
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher_hozoor"
        android:label="حضور و غیاب"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity android:name=".MainActivity" android:exported="true">
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
            <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/file_paths" />
        </provider>
    </application>
</manifest>
''',

    "android-app/app/src/main/res/xml/file_paths.xml": r'''<?xml version="1.0" encoding="utf-8"?>
<paths><cache-path name="exports" path="exports/" /></paths>
''',

    "android-app/app/src/main/res/drawable/ic_launcher_hozoor.xml": r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#146C56" android:pathData="M24,8 L84,8 C93,8 100,15 100,24 L100,84 C100,93 93,100 84,100 L24,100 C15,100 8,93 8,84 L8,24 C8,15 15,8 24,8 Z" />
    <path android:fillColor="#FFFFFF" android:pathData="M45,72 L27,54 L34,47 L45,58 L74,29 L81,36 Z" />
</vector>
''',

    "android-app/app/src/main/assets/sample_school.csv": r'''ردیف,نام مدرسه,رشته,پایه,شعبه,نام,نام خانوادگی,نام پدر,کد ملی,شماره موبایل
1,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,1,محمد,آزادی,هارون,4700153423,9170327544
2,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,1,مهدی,بهروزی,بهرام,5150303194,9172893258
3,آموزشگاه نمونه,صنایع شیمیایی,یازدهم,2,ابراهیم,احمدی,راشد,3560366232,9179739834
4,آموزشگاه نمونه,الکتروتکنیک,دهم,1,امیرعلی,آریان فر,محمد,4700157801,9173629540
5,آموزشگاه نمونه,الکتروتکنیک,دوازدهم,1,بنیامین,طاهری,فرشاد,441746977,9124409109
6,آموزشگاه نمونه,ساختمان,یازدهم,1,امیرحسین,ابراهیمی,محمد,4700154403,9173643201
7,آموزشگاه نمونه,ساختمان,دوازدهم,1,ابراهیم,رکابکار,عبدالملک,4700139617,9173642185
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
        engine = AttendanceEngine(File(filesDir, "hozoor_attendance.db").absolutePath)
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/MainActivity.kt": r'''package ir.hozoor.app

import android.app.ActivityManager
import android.content.Context
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
                am.isLowRamDevice || pm.isPowerSaveMode
            }
            val vm: AttendanceViewModel = viewModel(factory = object : ViewModelProvider.Factory {
                @Suppress("UNCHECKED_CAST")
                override fun <T : ViewModel> create(modelClass: Class<T>): T = AttendanceViewModel(app.engine) as T
            })
            val uiState by vm.uiState.collectAsStateWithLifecycle()
            val systemDark = isSystemInDarkTheme()
            val useDark = when (uiState.themeMode) {
                "dark" -> true
                "light" -> false
                else -> systemDark
            }
            HozoorExpressiveTheme(darkTheme = useDark, dynamicColor = uiState.dynamicColorEnabled, reduceMotion = reduceMotion) {
                AttendanceScreen(viewModel = vm, isDarkTheme = useDark)
            }
        }
    }
}
''',

    "android-app/app/src/main/java/ir/hozoor/app/util/FileShareHelper.kt": r'''package ir.hozoor.app.util

import android.content.ClipData
import android.content.ClipboardManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.ContactsContract
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import java.io.File

object FileShareHelper {
    private val KNOWN_CONTACTS_PACKAGES = listOf(
        "com.google.android.contacts",
        "com.samsung.android.app.contacts",
        "com.android.contacts",
        "com.miui.contacts",
        "com.huawei.contacts",
        "com.hihonor.contacts",
        "com.oplus.contacts"
    )
    private val BLOCKED_PICKER_KEYWORDS = listOf("file", "explorer", "document", "manager", "gallery", "media", "drive")

    fun shareBytesAsFile(context: Context, fileName: String, mimeType: String, bytes: ByteArray, chooserTitle: String) {
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

    /**
     * انتخابگر مطمئن مخاطبین برای همه برندها (شیائومی MIUI/HyperOS، سامسونگ، هواوی، آنر، اوپو، پیکسل).
     * مستقیماً پکیج و کامپوننت اپ مخاطبین اصلی سیستم را پین می‌کند تا فایل منیجر شیائومی هیچ‌گاه باز نشود.
     */
    fun createPickPhoneContactIntent(context: Context): Intent {
        val intent = Intent(Intent.ACTION_PICK).apply {
            type = ContactsContract.CommonDataKinds.Phone.CONTENT_TYPE
        }
        val pm = context.packageManager
        val resolved = runCatching { pm.queryIntentActivities(intent, 0) }.getOrDefault(emptyList())
        val safeList = resolved.filter { info ->
            val pkg = info.activityInfo.packageName.lowercase()
            BLOCKED_PICKER_KEYWORDS.none { bad -> pkg.contains(bad) }
        }
        val best = KNOWN_CONTACTS_PACKAGES.firstNotNullOfOrNull { known ->
            safeList.firstOrNull { it.activityInfo.packageName.equals(known, ignoreCase = true) }
        } ?: safeList.firstOrNull { info ->
            val pkg = info.activityInfo.packageName.lowercase()
            pkg.contains("contact") || pkg.contains("dialer") || pkg.contains("phone")
        } ?: safeList.firstOrNull()

        return if (best != null) {
            intent.apply {
                setPackage(best.activityInfo.packageName)
                component = ComponentName(best.activityInfo.packageName, best.activityInfo.name)
            }
        } else {
            Intent(Intent.ACTION_PICK, ContactsContract.CommonDataKinds.Phone.CONTENT_URI)
        }
    }

    /** استخراج ایمن نام و شماره با پشتیبانی کامل از ارقام فارسی/عربی، +98 و 0098 و تمام رام‌ها */
    fun extractPhoneContact(context: Context, uri: Uri): Pair<String, String>? {
        val proj = arrayOf(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER)
        val firstTry = runCatching {
            context.contentResolver.query(uri, proj, null, null, null)?.use { c ->
                if (c.moveToFirst()) {
                    val name = c.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME).takeIf { it >= 0 }?.let { c.getString(it) }.orEmpty()
                    val num = c.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER).takeIf { it >= 0 }?.let { c.getString(it) }.orEmpty()
                    cleanIranPhone(num)?.let { cleaned -> name.ifBlank { "مخاطب" } to cleaned }
                } else null
            }
        }.getOrNull()
        if (firstTry != null) return firstTry

        // فالبک برای رام‌هایی که ستون متفاوتی برمی‌گردانند
        return runCatching {
            context.contentResolver.query(uri, null, null, null, null)?.use { c ->
                if (c.moveToFirst()) {
                    val name = listOf("display_name", "display_name_primary", "name")
                        .firstNotNullOfOrNull { col -> c.getColumnIndex(col).takeIf { it >= 0 }?.let { c.getString(it) } }
                        .orEmpty()
                    val rawNum = listOf("data1", "number", "phone")
                        .firstNotNullOfOrNull { col -> c.getColumnIndex(col).takeIf { it >= 0 }?.let { c.getString(it) } }
                        .orEmpty()
                    cleanIranPhone(rawNum)?.let { cleaned -> name.ifBlank { "مخاطب" } to cleaned }
                } else null
            }
        }.getOrNull()
    }

    private fun cleanIranPhone(raw: String): String? {
        val normalized = normalizePersianSearch(raw)
        val hasPlus98 = normalized.contains("+98")
        val digits = normalized.filter { it.isDigit() }
        val result = when {
            hasPlus98 && digits.startsWith("98") -> "0" + digits.removePrefix("98")
            digits.startsWith("0098") -> "0" + digits.removePrefix("0098")
            digits.startsWith("98") && digits.length == 12 -> "0" + digits.removePrefix("98")
            digits.startsWith("9") && digits.length == 10 -> "0$digits"
            else -> digits
        }
        return result.takeIf { it.length >= 7 }
    }

    fun openSmsApp(context: Context, phone: String, body: String): Boolean {
        val clean = phone.trim()
        val list = listOf(
            Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:$clean")).apply { putExtra("sms_body", body) },
            Intent(Intent.ACTION_VIEW, Uri.parse("sms:$clean")).apply { putExtra("sms_body", body) },
            Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, body) }
        )
        for (i in list) {
            runCatching {
                context.startActivity(if (i.action == Intent.ACTION_SEND) Intent.createChooser(i, "ارسال پیام") else i)
                return true
            }
        }
        return false
    }

    fun openWhatsApp(context: Context, phone: String, body: String): Boolean {
        val d = normalizePersianSearch(phone).filter { it.isDigit() }
        val intl = when {
            d.startsWith("0") && d.length == 11 -> "98" + d.drop(1)
            d.startsWith("9") && d.length == 10 -> "98$d"
            else -> d
        }
        val url = if (intl.isNotBlank()) "https://wa.me/$intl?text=${Uri.encode(body)}" else "https://wa.me/?text=${Uri.encode(body)}"
        return runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))); true }
            .getOrElse { shareText(context, body, "ارسال پیام"); false }
    }

    fun shareText(context: Context, text: String, title: String) {
        val intent = Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, text) }
        context.startActivity(Intent.createChooser(intent, title))
    }

    fun copyToClipboard(context: Context, label: String, text: String) {
        val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        cm.setPrimaryClip(ClipData.newPlainText(label, text))
    }

    fun normalizePersianSearch(text: String): String = text.trim()
        .replace('ي', 'ی').replace('ى', 'ی').replace('ك', 'ک')
        .replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4')
        .replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')
        .replace('٠', '0').replace('١', '1').replace('٢', '2').replace('٣', '3').replace('٤', '4')
        .replace('٥', '5').replace('٦', '6').replace('٧', '7').replace('٨', '8').replace('٩', '9')
        .lowercase()

    fun resolveFileName(context: Context, uri: Uri): String {
        context.contentResolver.query(uri, null, null, null, null)?.use { c ->
            val idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx >= 0 && c.moveToFirst()) return c.getString(idx) ?: "students.xlsx"
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
    val Present = Color(0xFF16A34A)
    val OnPresent = Color.White
    val Absent = Color(0xFFDC2626)
    val OnAbsent = Color.White
    val Late = Color(0xFFF59E0B)
    val OnLate = Color(0xFF1A1A1A)
    val Excused = Color(0xFF2563EB)
    val OnExcused = Color.White
    val LeftClass = Color(0xFF9333EA)
    val OnLeftClass = Color.White
}

private val ExpressiveDarkFallback = darkColorScheme(
    primary = Color(0xFF4ADE80), onPrimary = Color(0xFF00391A),
    primaryContainer = Color(0xFF0F5132), onPrimaryContainer = Color(0xFFC2F7D4),
    secondary = Color(0xFF93C5FD), onSecondary = Color(0xFF003063),
    secondaryContainer = Color(0xFF1E3A5F), onSecondaryContainer = Color(0xFFD6E7FF),
    tertiary = Color(0xFFD8B4FE), onTertiary = Color(0xFF3B0764),
    tertiaryContainer = Color(0xFF4C1D95), onTertiaryContainer = Color(0xFFF3E8FF),
    background = Color(0xFF0E1311), surface = Color(0xFF0E1311),
    surfaceContainerLow = Color(0xFF161D1A), surfaceContainer = Color(0xFF1C2521), surfaceContainerHigh = Color(0xFF232E29)
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
        MaterialExpressiveTheme(colorScheme = colorScheme, motionScheme = motionScheme, typography = HozoorTypography, content = content)
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
import uniffi.hozoor_core.BackupStats
import uniffi.hozoor_core.ClassAnalytics
import uniffi.hozoor_core.ClassGroup
import uniffi.hozoor_core.GradeCategory
import uniffi.hozoor_core.JalaliMonthGrid
import uniffi.hozoor_core.MonthlyClassReport
import uniffi.hozoor_core.MonthlyStudentStat
import uniffi.hozoor_core.Period
import uniffi.hozoor_core.PeriodSummary
import uniffi.hozoor_core.PrincipalReportBundle
import uniffi.hozoor_core.SavedContact
import uniffi.hozoor_core.StudentAttendanceRow
import uniffi.hozoor_core.StudentGradeRow
import uniffi.hozoor_core.StudentMonthlyEvent
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
    val recipientName: String = "",
    val searchQuery: String = "",
    val gradebookSearchQuery: String = "",
    val monthlySearchQuery: String = "",
    val isPeriodSaved: Boolean = false,
    val students: List<StudentAttendanceRow> = emptyList(),
    val summary: PeriodSummary = PeriodSummary(0, 0, 0, 0, 0, 0),
    val gradeCategories: List<GradeCategory> = emptyList(),
    val selectedGradeCategoryId: Long = 0L,
    val classGrades: List<StudentGradeRow> = emptyList(),
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
    val inspectingMonthlyStudent: MonthlyStudentStat? = null,
    val inspectingMonthlyEvents: List<StudentMonthlyEvent> = emptyList(),
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
    fun updateGradebookSearch(q: String) { _uiState.update { it.copy(gradebookSearchQuery = q) } }
    fun updateMonthlySearch(q: String) { _uiState.update { it.copy(monthlySearchQuery = q) } }

    fun openStudentMonthlyDetails(stat: MonthlyStudentStat) {
        val st = _uiState.value
        _uiState.update { it.copy(inspectingMonthlyStudent = stat, inspectingMonthlyEvents = emptyList()) }
        viewModelScope.launch {
            val events = withContext(Dispatchers.IO) { engine.getStudentMonthlyDetails(stat.studentId, st.monthlyYear, st.monthlyMonth) }
            _uiState.update { it.copy(inspectingMonthlyEvents = events) }
        }
    }

    fun closeStudentMonthlyDetails() { _uiState.update { it.copy(inspectingMonthlyStudent = null, inspectingMonthlyEvents = emptyList()) } }

    fun setStudentStatus(studentId: Long, status: AttendanceStatus, eventTime: String = "", note: String = "") {
        val st = _uiState.value
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                engine.setAttendance(studentId, st.selectedDate.toString(), st.selectedPeriod, status, eventTime, note, st.teacherName, st.lessonName, st.classTime)
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
            loadAttendanceSnapshot(); showMessage("همه $n دانش‌آموز در حالت حاضر ثبت شدند")
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

    fun selectGradeCategory(catId: Long) { _uiState.update { it.copy(selectedGradeCategoryId = catId) }; loadGradebook() }

    fun addGradeCategory(name: String) {
        viewModelScope.launch {
            try {
                val newId = withContext(Dispatchers.IO) { engine.addGradeCategory(name) }
                val cats = withContext(Dispatchers.IO) { engine.getGradeCategories() }
                _uiState.update { it.copy(gradeCategories = cats, selectedGradeCategoryId = newId) }
                loadGradebook(); showMessage("عنوان «$name» اضافه شد")
            } catch (e: Exception) { showMessage(e.message ?: "خطا") }
        }
    }

    fun deleteGradeCategory(catId: Long) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { engine.deleteGradeCategory(catId) }
            val cats = withContext(Dispatchers.IO) { engine.getGradeCategories() }
            _uiState.update { it.copy(gradeCategories = cats, selectedGradeCategoryId = cats.firstOrNull()?.id ?: 0L) }
            loadGradebook(); showMessage("عنوان نمره حذف شد")
        }
    }

    fun setStudentGrade(studentId: Long, categoryId: Long, score: String, note: String) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) { engine.setStudentGrade(studentId, categoryId, score, note) }
            loadGradebook(); loadAttendanceSnapshot(); showMessage("نمره ثبت شد")
        }
    }

    fun exportGradebookExcel(onReady: (String, ByteArray) -> Unit) {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch { onReady("grades_${cls.grade}_${cls.section}.xlsx", withContext(Dispatchers.IO) { engine.exportGradebookXlsx(cls.major, cls.grade, cls.section) }) }
    }

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
            _uiState.update { it.copy(savedContacts = withContext(Dispatchers.IO) { engine.getSavedContacts() }) }
        }
    }

    fun addStudentToCurrentClass(f: String, l: String, fa: String, nid: String, mob: String) {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch {
            try { withContext(Dispatchers.IO) { engine.addStudent(cls.schoolName, cls.major, cls.grade, cls.section, f, l, fa, nid, mob) }; refreshClassesAndData(); showMessage("دانش‌آموز اضافه شد") }
            catch (e: Exception) { showMessage(e.message ?: "خطا") }
        }
    }

    fun updateStudent(id: Long, f: String, l: String, fa: String, nid: String, mob: String) {
        viewModelScope.launch {
            try { withContext(Dispatchers.IO) { engine.updateStudent(id, f, l, fa, nid, mob) }; loadAttendanceSnapshot(); showMessage("اطلاعات ذخیره شد") }
            catch (e: Exception) { showMessage(e.message ?: "خطا") }
        }
    }

    fun deleteStudent(id: Long) { viewModelScope.launch { withContext(Dispatchers.IO) { engine.deleteStudent(id) }; refreshClassesAndData(); showMessage("دانش‌آموز حذف شد") } }
    fun deleteCurrentClass() {
        val cls = _uiState.value.selectedClass ?: return
        viewModelScope.launch { val n = withContext(Dispatchers.IO) { engine.deleteClass(cls.major, cls.grade, cls.section) }; refreshClassesAndData(); showMessage("کلاس و $n دانش‌آموز حذف شدند") }
    }

    fun importFileBytes(name: String, bytes: ByteArray, replace: Boolean) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try { val rep = withContext(Dispatchers.IO) { engine.importFileBytes(name, bytes, replace) }; refreshClassesAndData(); showMessage("${rep.importedCount} دانش‌آموز در ${rep.classesCount} کلاس وارد شد") }
            catch (e: Exception) { _uiState.update { it.copy(isLoading = false) }; showMessage("خطا: ${e.message}") }
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
        viewModelScope.launch { onReady("hozoor_backup_$d.json", withContext(Dispatchers.IO) { engine.exportBackupJson() }.toByteArray(Charsets.UTF_8)) }
    }

    fun exportTemplateExcel(onReady: (String, ByteArray) -> Unit) {
        viewModelScope.launch { onReady("نمونه_ورود_دانش_آموزان.xlsx", withContext(Dispatchers.IO) { engine.exportTemplateXlsx() }) }
    }

    fun prepareExportSheet(wholeSchool: Boolean = _uiState.value.reportWholeSchool) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        _uiState.update { it.copy(reportWholeSchool = wholeSchool, sheetFeedback = null) }
        viewModelScope.launch {
            val (bundle, stats, contacts) = withContext(Dispatchers.IO) {
                Triple(engine.generatePrincipalReport(cls.major, cls.grade, cls.section, st.selectedDate.toString(), wholeSchool, st.teacherName), engine.getBackupStats(), engine.getSavedContacts())
            }
            _uiState.update { it.copy(principalReport = bundle, backupStats = stats, savedContacts = contacts) }
        }
    }

    fun generatePeriodGroupMessage(target: AttendanceStatus, onReady: (String) -> Unit) {
        val st = _uiState.value; val cls = st.selectedClass ?: return
        _uiState.update { it.copy(sheetFeedback = null) }
        viewModelScope.launch {
            try {
                val msg = withContext(Dispatchers.IO) { engine.generatePeriodGroupMessage(cls.major, cls.grade, cls.section, st.selectedDate.toString(), st.selectedPeriod, target, st.teacherName, st.lessonName, st.reportWholeSchool) }
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
''',
}


def main():
    for rel, content in FILES.items():
        p = Path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
        print(f"Created: {rel}")
    print(f"\nPart 2 (Android Base v5.1) done: {len(FILES)} files.")


if __name__ == "__main__":
    main()
