plugins {
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
        versionCode = 1
        versionName = "1.1.0"
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
