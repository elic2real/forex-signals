# Add project specific ProGuard rules here.

# Keep OkHttp classes
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }
-dontwarn okhttp3.**

# Keep Gson classes for JSON serialization
-keepattributes Signature
-keepattributes *Annotation*
-keep class sun.misc.Unsafe { *; }
-keep class com.google.gson.** { *; }

# Keep our model classes for Gson
-keep class com.forexalertpro.mobile.models.** { *; }
-keep class com.tradingsignals.alerts.models.** { *; }

# Keep Firebase classes
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }

# Keep our service classes
-keep class com.forexalertpro.mobile.services.** { *; }
-keep class com.tradingsignals.alerts.services.** { *; }

# Keep BuildConfig
-keep class **.BuildConfig { *; }

# Keep serialized names for Gson
-keepclassmembers,allowobfuscation class * {
  @com.google.gson.annotations.SerializedName <fields>;
}