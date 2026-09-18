#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include "model.h"
#include "calibration.h"
#ifndef ROLE_LEADER
#define ROLE_LEADER 1
#endif
constexpr uint8_t MUX=0x70,ENC=0x36,PCA=0x40;
constexpr int SDA_PIN=21,SCL_PIN=22,OE_PIN=25;
Preferences prefs;uint16_t zeros[6]={};int8_t signs[6]={1,1,1,1,1,1};
bool calibrated=false,armed=false,driverOK=false,haveTarget=false;
uint32_t tick=0,lastTarget=0;float goal[6],current[6];
char line[128];size_t used=0;bool overflow=false;uint8_t prescale;
bool writeReg(uint8_t addr,uint8_t reg,uint8_t value){Wire.beginTransmission(addr);Wire.write(reg);Wire.write(value);return Wire.endTransmission()==0;}
int readReg(uint8_t addr,uint8_t reg){Wire.beginTransmission(addr);Wire.write(reg);if(Wire.endTransmission(false))return -1;if(Wire.requestFrom(addr,uint8_t(1))!=1)return -1;return Wire.read();}
void stop(const char *why){digitalWrite(OE_PIN,HIGH);armed=false;haveTarget=false;Serial.print("STOP ");Serial.println(why);}
bool encoder(int channel,uint16_t &raw){
 Wire.beginTransmission(MUX);Wire.write(uint8_t(1<<channel));if(Wire.endTransmission())return false;
 int s=readReg(ENC,0x0B);if(s<0||!(s&0x20)||(s&0x18))return false;
 Wire.beginTransmission(ENC);Wire.write(0x0C);if(Wire.endTransmission(false))return false;
 if(Wire.requestFrom(ENC,uint8_t(2))!=2)return false;raw=((Wire.read()&15)<<8)|Wire.read();return true;
}
bool sample(uint16_t *raw){for(int i=0;i<6;i++)if(!encoder(i,raw[i])){Serial.print("FAULT encoder ");Serial.println(i);return false;}return true;}
bool validPulse(int i,float q){float p=model::pulse(q,SERVO_ZERO_US[i],US_PER_DEGREE[i],SERVO_SIGN[i]);return isfinite(p)&&p>=PULSE_MIN_US[i]&&p<=PULSE_MAX_US[i];}
bool servo(int i,float q){
 if(!validPulse(i,q))return false;float us=model::pulse(q,SERVO_ZERO_US[i],US_PER_DEGREE[i],SERVO_SIGN[i]);
 uint16_t count=lroundf(us*PCA_CLOCK_HZ/(1e6f*(prescale+1)));
 Wire.beginTransmission(PCA);Wire.write(uint8_t(6+4*i));Wire.write(0);Wire.write(0);Wire.write(count&255);Wire.write(count>>8);return Wire.endTransmission()==0;
}
void command(){
 if(ROLE_LEADER){
  if(!strcmp(line,"ZERO")){uint16_t raw[6];if(!sample(raw))return;memcpy(zeros,raw,sizeof zeros);prefs.putBytes("zeros",zeros,sizeof zeros);calibrated=true;Serial.println("ZERO saved at displayed home pose");return;}
  int j,sign,end=0;if(sscanf(line,"SIGN %d %d %n",&j,&sign,&end)==2&&line[end]==0&&j>=0&&j<6&&(sign==1||sign==-1)){signs[j]=sign;prefs.putBytes("signs",signs,sizeof signs);Serial.println("SIGN saved");return;}
  if(!strcmp(line,"FORGET")){prefs.remove("zeros");calibrated=false;Serial.println("RAW mode");return;}
  Serial.println("COMMANDS: ZERO | SIGN axis +/-1 | FORGET");return;
 }
 if(!strcmp(line,"STOP")){stop("user");return;}
 if(!strcmp(line,"ARM")){
  if(!FOLLOWER_CALIBRATED){stop("pulse_calibration_required");return;}
  if(!driverOK||!haveTarget||model::stale(millis(),lastTarget)){stop("fresh_home_target_required");return;}
  for(int i=0;i<6;i++)if(fabsf(goal[i]-model::home[i])>3){stop("home_pose_required");return;}
  memcpy(current,goal,sizeof goal);for(int i=0;i<6;i++)if(!servo(i,current[i])){stop("i2c_or_pulse_fault");return;}
  armed=true;digitalWrite(OE_PIN,LOW);Serial.println("ARMED");return;
 }
 float q[6];int end=0;
 if(sscanf(line,"Q %f %f %f %f %f %f %n",q,q+1,q+2,q+3,q+4,q+5,&end)==6&&line[end]==0&&model::valid(q)){
  for(int i=0;i<6;i++)if(!validPulse(i,q[i])){stop("pulse_limit");return;}
  memcpy(goal,q,sizeof q);lastTarget=millis();haveTarget=true;return;
 }
 stop("invalid_target");
}
void setup(){
 pinMode(OE_PIN,OUTPUT);digitalWrite(OE_PIN,HIGH);Serial.begin(115200);Wire.begin(SDA_PIN,SCL_PIN);Wire.setClock(100000);Wire.setTimeOut(20);
 memcpy(goal,model::home,sizeof goal);memcpy(current,goal,sizeof current);
 if(ROLE_LEADER){prefs.begin("thenar-L1",false);calibrated=prefs.getBytesLength("zeros")==sizeof zeros;if(calibrated)prefs.getBytes("zeros",zeros,sizeof zeros);if(prefs.getBytesLength("signs")==sizeof signs)prefs.getBytes("signs",signs,sizeof signs);for(int i=0;i<6;i++)if(signs[i]!=1&&signs[i]!=-1)signs[i]=1;}
 else {prescale=uint8_t(lroundf(PCA_CLOCK_HZ/(4096*50))-1);driverOK=writeReg(PCA,0,0x10)&&writeReg(PCA,0xFE,prescale)&&writeReg(PCA,1,4)&&writeReg(PCA,0,0x20);delay(5);}
 Serial.println(ROLE_LEADER?"THENAR AS5600 LEADER L1":"THENAR MG996R FOLLOWER R3 DISARMED");
}
void loop(){
 while(Serial.available()){
  char c=Serial.read();if(c=='\r')continue;
  if(c=='\n'){line[used]=0;if(overflow){if(ROLE_LEADER)Serial.println("FAULT line_overflow");else stop("line_overflow");}else if(used)command();used=0;overflow=false;}
  else if(used<sizeof line-1)line[used++]=c;else overflow=true;
 }
 uint32_t now=millis();if(!ROLE_LEADER&&armed&&model::stale(now,lastTarget))stop("watchdog");
 if(uint32_t(now-tick)<20)return;tick=now;
 if(ROLE_LEADER){
  uint16_t raw[6];if(!sample(raw))return;float q[6];for(int i=0;i<6;i++)q[i]=model::home[i]+signs[i]*model::wrappedDegrees(raw[i],zeros[i]);
  if(calibrated&&!model::valid(q)){Serial.println("FAULT joint_range");return;}
  Serial.print(calibrated?"L":"RAW");for(int i=0;i<6;i++){Serial.print(' ');if(calibrated)Serial.print(q[i],3);else Serial.print(raw[i]);}Serial.println();
 }else if(armed){for(int i=0;i<6;i++){current[i]=model::slew(current[i],goal[i]);if(!servo(i,current[i])){stop("i2c_or_pulse_fault");break;}}}
}
