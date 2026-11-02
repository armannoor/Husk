package android.content;

/** The callback a broadcast's sender gets when a receiver finishes (system-internal). */
public interface IIntentReceiver extends android.os.IInterface {
    void performReceive(Intent intent, int resultCode, String data, android.os.Bundle extras,
                        boolean ordered, boolean sticky, int sendingUser);
}
