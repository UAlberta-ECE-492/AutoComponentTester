#define POWER_PIN 13
#define RED_ON 80
#define GRN_ON 8

enum ALOG_PINS
{
    CUR_SRC = A0,
};
enum RELAY_PINS
{
    WG1_CTRL = 2,
    WG2_CTRL = 3,
    OSC_CTRL = 4,
    V_PLUS_CTRL = 5,
    V_MINUS_CTRL = 6,
};

const int RELAY_PINS[] = {
    RELAY_PINS::WG1_CTRL,
    RELAY_PINS::WG2_CTRL,
    RELAY_PINS::OSC_CTRL,
    RELAY_PINS::V_PLUS_CTRL,
    RELAY_PINS::V_MINUS_CTRL,
};

enum RELAY_STATES
{
    STATE_OFF = 0,
    STATE_WG1 = 1,
    STATE_WG2 = 2,
    STATE_SCOPE_TO_GND = 3,
    STATE_SCOPE_TO_WG1 = 4,
    STATE_V_PLUS = 5,
    STATE_V_MINUS = 6,
    TOTAL_RELAY_STATES,
};

enum COMMANDS
{
    SET_RELAY_STATE = 0,
    CHECK_CURRENT = 1,
    SET_CAL_STAT = 2
};

enum LED_PINS
{
    AD_RED = 9,
    AD_GRN = 10,
    CUR_RED = 11,
    CUR_GRN = 12
};

enum AD_STATE
{
    AD_NOT_READY,
    AD_READY,
    CALIBRATING,
    CAL_GOOD,
    ERROR
};

enum CUR_STATE
{
    CUR_NOT_READY,
    CUR_READY,
    GOOD,
    BAD
};

bool power_connected = false;
double current = 0.;
enum CUR_STATE current_status = CUR_STATE::CUR_NOT_READY;
enum AD_STATE ad_status = AD_STATE::AD_NOT_READY;
bool cmd_cur_grn_on = false;
bool cur_grn_state = false;
unsigned long cur_grn_clk = 0;

void setup()
{
    Serial.begin(9600);
    setup_relay_pins();
    setup_LED_pins();
    pinMode(POWER_PIN, INPUT);
    pinMode(ALOG_PINS::CUR_SRC, INPUT);
    power_connected = !digitalRead(POWER_PIN); // forces LEDs to update on boot
    Serial.write("ready!\n");
}


void pwmPinMs(int digitalPin, float dutyCycle, unsigned long periodMs, int brightness = 255){
    unsigned long onTime = static_cast<unsigned long>(dutyCycle * float(periodMs));
    unsigned long curTime = millis();
    if(curTime % periodMs <= onTime){
        analogWrite(digitalPin, brightness);
    }
    else{
        digitalWrite(digitalPin, LOW);
    }
}


void updateLedColors(){
  if(power_connected && ad_status == AD_STATE::ERROR){
    pwmPinMs(LED_PINS::AD_RED, 0.70, 3000, RED_ON);
  }
  else if(ad_status == AD_STATE::CALIBRATING){
    pwmPinMs(LED_PINS::AD_RED, 0.70, 2000, RED_ON);
    pwmPinMs(LED_PINS::AD_GRN, 0.70, 2000, GRN_ON);
  }
  if(!power_connected){
    pwmPinMs(LED_PINS::AD_RED, 0.50, 1000, RED_ON);
  }
}
void loop()
{
    check_power_connection();
    cur_grn_pwm();
    updateLedColors();
    if (power_connected)
    {
        check_current();
    }
    processIncomingSerial();
}

int get_total_pins()
{
    return sizeof(RELAY_PINS) / sizeof(RELAY_PINS[0]);
}
void setup_relay_pins()
{
    for (int i = 0; i < get_total_pins(); i++)
    {
        pinMode(RELAY_PINS[i], OUTPUT);
    }
}

void setup_LED_pins()
{
    pinMode(LED_PINS::AD_GRN, OUTPUT);
    pinMode(LED_PINS::AD_RED, OUTPUT);
    pinMode(LED_PINS::CUR_GRN, OUTPUT);
    pinMode(LED_PINS::CUR_RED, OUTPUT);
}

void check_power_connection()
{
    bool power = digitalRead(POWER_PIN);
    if (!power_connected && power) //power just got connected
    {
        power_connected = true;
        if (ad_status == AD_STATE::AD_NOT_READY)
        {
            update_ad_led(AD_STATE::AD_READY);
        }
        if (current_status == CUR_STATE::CUR_NOT_READY)
        {
            update_cur_led(CUR_STATE::CUR_READY);
        }
    }
    else if (power_connected && !power)
    {
        power_connected = false;
        update_ad_led(AD_STATE::AD_NOT_READY);
        update_cur_led(CUR_STATE::CUR_NOT_READY);
    }
}

int update_ad_led(enum AD_STATE new_status)
{
    ad_status = new_status;
    switch (ad_status)
    {
        case AD_STATE::AD_NOT_READY:
        {
            analogWrite(LED_PINS::AD_RED, RED_ON);
            analogWrite(LED_PINS::AD_GRN, 0);
            break;
        }
        case AD_STATE::AD_READY:
        {
            analogWrite(LED_PINS::AD_RED, RED_ON+20);
            analogWrite(LED_PINS::AD_GRN, GRN_ON);
            break;
        }
        case AD_STATE::CALIBRATING:
        {
            analogWrite(LED_PINS::AD_RED, RED_ON);
            analogWrite(LED_PINS::AD_GRN, GRN_ON);
            break;
        }
        case AD_STATE::CAL_GOOD:
        {
            analogWrite(LED_PINS::AD_RED, 0);
            analogWrite(LED_PINS::AD_GRN, GRN_ON);
            break;
        }
        case AD_STATE::ERROR:
        {
            analogWrite(LED_PINS::AD_RED, RED_ON);
            analogWrite(LED_PINS::AD_GRN, 0);
            break;
        }
        default:
        {
            return 0;
        }
    }
    return 1;
}
void update_cur_led(enum CUR_STATE new_status)
{
    current_status = new_status;
    switch (current_status)
    {
        case CUR_STATE::CUR_NOT_READY:
        {
            analogWrite(LED_PINS::CUR_RED, RED_ON);
            cmd_cur_grn_on = false;
            break;
        }
        case CUR_STATE::CUR_READY:
        {
            analogWrite(LED_PINS::CUR_RED, 0);
            cmd_cur_grn_on = false;
            break;
        }
        case CUR_STATE::GOOD:
        {
            analogWrite(LED_PINS::CUR_RED, 0);
            cmd_cur_grn_on = true;
            break;
        }
        case CUR_STATE::BAD:
        {
            analogWrite(LED_PINS::CUR_RED, RED_ON);
            cmd_cur_grn_on = false;
            break;
        }
    }
}

void cur_grn_pwm()
{
    if (cmd_cur_grn_on)
    {
        if ((cur_grn_state == true) && (millis() - cur_grn_clk >= 1))
        {
            digitalWrite(LED_PINS::CUR_GRN, false);
            cur_grn_state = false;
            cur_grn_clk = millis();
        }
        else if ((cur_grn_state == false) && (millis() - cur_grn_clk >= 12)) 
        {
            digitalWrite(LED_PINS::CUR_GRN, true);
            cur_grn_state = true;
            cur_grn_clk = millis();
            }
    }
    else
    {
        digitalWrite(LED_PINS::CUR_GRN, false);
    }
}

void check_current()
{
    uint64_t current_sum = 0;
    for (int i = 0; i < 10; i++)
    {
        current_sum += analogRead(ALOG_PINS::CUR_SRC);
    }

    current = current_sum * 0.12520032051282l; // 5V/1025 divs / 0.0039 Mohms / 10 samples

    if (489.9938l <= current && current <= 552.5462l) // 521.27 uA setpoint within 6% (read 392 -417- 441)
    {
        update_cur_led(CUR_STATE::GOOD);
    }
    else if (current < 50.l)
    {
        update_cur_led(CUR_STATE::CUR_READY);
    }
    else
    {
        update_cur_led(CUR_STATE::BAD);
    }
}

void turn_all_off()
{

    for (int i = 0; i < get_total_pins(); i++)
    {
        digitalWrite(RELAY_PINS[i], LOW);
    }
}

int change_relay_to_state(RELAY_STATES state)
{
    turn_all_off();
    switch (state)
    {
    case RELAY_STATES::STATE_OFF:
    {
        Serial.write("1|All relays have been reset");
        break;
    }
    case RELAY_STATES::STATE_WG1:
    {
        digitalWrite(RELAY_PINS::WG1_CTRL, HIGH);
        Serial.write("1|WG1 mode enabled");
        break;
    }
    case RELAY_STATES::STATE_WG2:
    {
        digitalWrite(RELAY_PINS::WG2_CTRL, HIGH);
        Serial.write("1|WG2 mode enabled");
        break;
    }
    case RELAY_STATES::STATE_SCOPE_TO_GND:
    {
        digitalWrite(RELAY_PINS::OSC_CTRL, LOW);
        Serial.write("1|SCOPE_TO_GND mode enabled");
        break;
    }
    case RELAY_STATES::STATE_SCOPE_TO_WG1:
    {
        digitalWrite(RELAY_PINS::OSC_CTRL, HIGH);
        Serial.write("1|STATE_SCOPE_TO_WG1 mode enabled");
        break;
    }
    case RELAY_STATES::STATE_V_PLUS:
    {
        digitalWrite(RELAY_PINS::V_PLUS_CTRL, HIGH);
        Serial.write("1|V_PLUS_CTRL mode enabled");
        break;
    }
    case RELAY_STATES::STATE_V_MINUS:
    {
        digitalWrite(RELAY_PINS::V_MINUS_CTRL, HIGH);
        Serial.write("1|STATE_V_MINUS mode enabled");
        break;
    }
    default:
    {
        return 0;
    }
    }
    return 1;
}


void processCommand(uint8_t command, uint8_t data)
{
    switch (command)
    {
    case SET_RELAY_STATE:
    {
        if (!power_connected)
        {
            Serial.write("0|Board power is not connected");
            break;
        }
        if (!change_relay_to_state(data))
        {
            // bad state specified
            Serial.write("0|Invalid relay state specified");
        }
        break;
    }
    case CHECK_CURRENT:
    {
        if (!power_connected)
        {
            Serial.write("0|Board power is not connected");
            break;
        }
        Serial.println(current);
        break;

    }
    case SET_CAL_STAT:
    {
        if (update_ad_led(data))
        {
            Serial.write("1|AD status updated");
        }
        else
        {
            Serial.write("0|AD status not recognized");
        }
        break;
        
    }
    default:
    {
        // bad state specified
        Serial.write("0|Invalid command specified");
        break;
    }
    }
}
constexpr int MAX_SERIAL_BYTES = 2;
uint8_t incomingBytes[MAX_SERIAL_BYTES];
int incomingBytesIdx = 0;
uint8_t stopByte = 0xFF;

void processIncomingSerial()
{
    static uint8_t incomingBytes[3];
    if (Serial.available())
    {
        int rbyte = Serial.read();
        // say what you got:
        if (rbyte < 0)
        {
            Serial.write("0|Internal error. Invalid byte read.");
            // handle error
            return;
        }
        uint8_t cByte = uint8_t(rbyte);
        if (cByte == 0xFF && incomingBytesIdx == MAX_SERIAL_BYTES)
        {
            int command = incomingBytes[0];
            int data = incomingBytes[1];
            processCommand(command, data);
            incomingBytesIdx = 0;
            return;
        }
        if (incomingBytesIdx >= MAX_SERIAL_BYTES)
        {
            // handle error
            Serial.write("0|Invalid data received. Expected a 0xFF end byte.");
            incomingBytesIdx = 0;
            return;
        }
        incomingBytes[incomingBytesIdx] = cByte;
        incomingBytesIdx += 1;
    }
}