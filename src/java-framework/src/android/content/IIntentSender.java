package android.content;

/** A pending send the system performs later on the app's behalf (system-internal). */
public interface IIntentSender extends android.os.IInterface {
    void send(int code, Intent intent, String resolvedType, IIntentReceiver finishedReceiver,
              String requiredPermission, android.os.Bundle options);
    void send(int code, Intent intent, String resolvedType, IIntentReceiver finishedReceiver,
              String requiredPermission, android.os.Bundle options, int userId);

    abstract class Stub extends android.os.Binder implements IIntentSender {
        public static IIntentSender asInterface(android.os.IBinder b) {
            if (b == null) return null;
            android.os.IInterface local = b.queryLocalInterface(DESCRIPTOR);
            return local instanceof IIntentSender ? (IIntentSender) local : new Stub() {};
        }
        public static final String DESCRIPTOR = "android.content.IIntentSender";
        public android.os.IBinder asBinder() { return this; }
        public void send(int code, Intent intent, String resolvedType, IIntentReceiver finishedReceiver,
                         String requiredPermission, android.os.Bundle options) {}
        public void send(int code, Intent intent, String resolvedType, IIntentReceiver finishedReceiver,
                         String requiredPermission, android.os.Bundle options, int userId) {}
    }
}
