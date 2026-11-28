package ir.hozoor.app.util

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
