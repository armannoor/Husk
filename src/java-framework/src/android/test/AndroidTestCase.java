package android.test;

/**
 * The old InstrumentationTestCase base class. Husk cannot run instrumentation,
 * but unit-test code that ships inside an app links against this class.
 */
public class AndroidTestCase {
    private android.content.Context mContext;
    public void setContext(android.content.Context c) { mContext = c; }
    public android.content.Context getContext() { return mContext; }
    public void testAndroidTestCaseSetupProperly() {}
    protected void setUp() throws java.lang.Exception {}
    protected void tearDown() throws java.lang.Exception {}
    public static void assertEquals(int a, int b) { if (a != b) fail("expected " + a + " but was " + b); }
    public static void assertEquals(long a, long b) { if (a != b) fail("expected " + a + " but was " + b); }
    public static void assertEquals(Object a, Object b) { if (a == null ? b != null : !a.equals(b)) fail("expected " + a + " but was " + b); }
    public static void assertEquals(String message, String a, String b) { if (a == null ? b != null : !a.equals(b)) fail(message); }
    public static void assertEquals(String a, String b) { assertEquals(null, a, b); }
    public static void assertEquals(String message, Object a, Object b) { if (a == null ? b != null : !a.equals(b)) fail(message); }
    public static void assertFalse(boolean b) { if (b) fail("expected false"); }
    public static void assertTrue(boolean b) { if (!b) fail("expected true"); }
    public static void assertNotNull(Object o) { if (o == null) fail("expected not null"); }
    public static void assertNotNull(String message, Object o) { if (o == null) fail(message); }
    public static void assertNull(Object o) { if (o != null) fail("expected null"); }
    public static void assertNull(String message, Object o) { if (o != null) fail(message); }
    public static void fail(String message) { throw new AssertionError(message); }
}
