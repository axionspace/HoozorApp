package ir.hozoor.app.util

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.provider.ContactsContract
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import java.io.File

object FileShareHelper {
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
     * ساخت Intent مطمئن انتخاب مخاطب برای همه گوشی‌ها (به‌ویژه رفع باگ شیائومی MIUI/HyperOS
     * که در حالت عادی فایل منیجر را باز می‌کرد). بدون نیاز به مجوز READ_CONTACTS.
     */
    fun createPickPhoneContactIntent(context: Context): Intent {
        val intent = Intent(Intent.ACTION_PICK).apply {
            type = ContactsContract.CommonDataKinds.Phone.CONTENT_TYPE
        }
        val pm = context.packageManager
        val resolved = runCatching { pm.queryIntentActivities(intent, 0) }.getOrDefault(emptyList())
        val realContactsApp = resolved.firstOrNull { info ->
            val pkg = info.activityInfo.packageName.lowercase()
            val notFileManager = !pkg.contains("file") && !pkg.contains("explorer") && !pkg.contains("document")
            notFileManager && (pkg.contains("contacts") || pkg.contains("dialer") || pkg.contains("phone"))
        } ?: resolved.firstOrNull { info ->
            val pkg = info.activityInfo.packageName.lowercase()
            !pkg.contains("file") && !pkg.contains("explorer") && !pkg.contains("document")
        }
        if (realContactsApp != null) {
            intent.setPackage(realContactsApp.activityInfo.packageName)
        }
        return intent
    }

    fun extractPhoneContact(context: Context, uri: Uri): Pair<String, String>? {
        val proj = arrayOf(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER)
        context.contentResolver.query(uri, proj, null, null, null)?.use { c ->
            if (c.moveToFirst()) {
                val nIdx = c.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                val pIdx = c.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                val name = if (nIdx >= 0) c.getString(nIdx).orEmpty() else ""
                val raw = if (pIdx >= 0) c.getString(pIdx).orEmpty() else ""
                val clean = raw.replace(Regex("[^0-9+]"), "")
                    .let { if (it.startsWith("+98")) "0" + it.removePrefix("+98") else it }
                    .replace(Regex("[^0-9]"), "")
                if (clean.isNotBlank()) return name.ifBlank { "مخاطب" } to clean
            }
        }
        return null
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
        val d = phone.filter { it.isDigit() }
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
        .lowercase()

    fun resolveFileName(context: Context, uri: Uri): String {
        context.contentResolver.query(uri, null, null, null, null)?.use { c ->
            val idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx >= 0 && c.moveToFirst()) return c.getString(idx) ?: "students.xlsx"
        }
        return "students.xlsx"
    }
}
