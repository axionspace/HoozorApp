package ir.hozoor.app.util

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
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

    /** باز کردن مطمئن برنامه پیامک روی تمام گوشی‌ها (شیائومی، سامسونگ، اندروید ۷ تا ۱۵) */
    fun openSmsApp(context: Context, phone: String, body: String): Boolean {
        val cleanPhone = phone.trim()
        val candidates = listOf(
            Intent(Intent.ACTION_SENDTO, Uri.parse("smsto:$cleanPhone")).apply { putExtra("sms_body", body) },
            Intent(Intent.ACTION_VIEW, Uri.parse("sms:$cleanPhone")).apply { putExtra("sms_body", body) },
            Intent(Intent.ACTION_SEND).apply { type = "text/plain"; putExtra(Intent.EXTRA_TEXT, body) }
        )
        for (intent in candidates) {
            runCatching {
                context.startActivity(if (intent.action == Intent.ACTION_SEND) Intent.createChooser(intent, "ارسال پیام") else intent)
                return true
            }
        }
        return false
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
        context.contentResolver.query(uri, null, null, null, null)?.use { c ->
            val idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx >= 0 && c.moveToFirst()) return c.getString(idx) ?: "students.xlsx"
        }
        return "students.xlsx"
    }
}
