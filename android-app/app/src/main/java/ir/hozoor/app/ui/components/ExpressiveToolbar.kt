package ir.hozoor.app.ui.components

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
                Icon(Icons.Rounded.UploadFile, "ورود اکسل یا CSV")
            }
        }
    ) {
        IconButton(onClick = onResetAllPresent) { Icon(Icons.Rounded.DoneAll, "همه حاضر") }
        IconButton(onClick = onCopyFromPrevious, enabled = selectedPeriod != Period.FIRST) { Icon(Icons.Rounded.ContentCopy, "کپی زنگ قبل") }
        IconButton(onClick = onAddStudent) { Icon(Icons.Rounded.PersonAdd, "افزودن دانش‌آموز") }
        IconButton(onClick = onOpenExportSheet) { Icon(Icons.Rounded.Share, "مرکز ارسال، مخاطبین و پشتیبان") }
    }
}
