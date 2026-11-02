package android.telephony;

/**
 * Huawei's hidden telephony extension. Nothing here can work on iOS; the
 * methods return the neutral values apps can cope with, so code that probes it
 * falls back to the public TelephonyManager.
 */
public class HwTelephonyManager {
    private static final HwTelephonyManager INSTANCE = new HwTelephonyManager();
    public static HwTelephonyManager getDefault() { return INSTANCE; }
    public int getPhoneCount() { return 1; }
    public int getDefault4GSlotId() { return 0; }
    public boolean isDualImsSupported() { return false; }
    public boolean isSupportVoLTE() { return false; }
    public boolean isNsaState(int slotId) { return false; }
    public String getMeid() { return null; }
    public String getImei(int slotId) { return null; }
}
