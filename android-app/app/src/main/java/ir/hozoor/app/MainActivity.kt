package ir.hozoor.app

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.remember
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
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

            HozoorExpressiveTheme(reduceMotion = reduceMotion) {
                val vm: AttendanceViewModel = viewModel(
                    factory = object : ViewModelProvider.Factory {
                        @Suppress("UNCHECKED_CAST")
                        override fun <T : ViewModel> create(modelClass: Class<T>): T {
                            return AttendanceViewModel(app.engine) as T
                        }
                    }
                )
                AttendanceScreen(viewModel = vm)
            }
        }
    }
}
