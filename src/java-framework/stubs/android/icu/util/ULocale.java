// A compile-time stub: android.icu.util.ULocale is in core-icu4j.jar on the
// boot class path at run time, but the JDK javac compiles against has no
// android.icu package.
package android.icu.util;

public class ULocale {
    private final String mId;
    public ULocale(String id) { mId = id; }
    public static ULocale forLanguageTag(String tag) { return new ULocale(tag); }
    public String toLanguageTag() { return mId == null ? "" : mId; }
    public String getBaseName() { return mId == null ? "" : mId; }
    public String toString() { return toLanguageTag(); }
}
