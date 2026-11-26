package ir.hozoor.app

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
