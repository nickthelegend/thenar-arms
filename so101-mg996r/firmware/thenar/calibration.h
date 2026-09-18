#pragma once
// Enable follower outputs only after unloaded pulse calibration and assembly fit.
constexpr bool FOLLOWER_CALIBRATED=false;
constexpr float SERVO_ZERO_US[6]={1500,1500,1500,1500,1500,1500};
constexpr float US_PER_DEGREE[6]={5.555556,5.555556,5.555556,5.555556,5.555556,5.555556};
constexpr int SERVO_SIGN[6]={1,1,1,1,1,1};
constexpr float PULSE_MIN_US[6]={1000,1000,1000,1000,1000,1000};
constexpr float PULSE_MAX_US[6]={2000,2000,2000,2000,2000,2000};
constexpr float PCA_CLOCK_HZ=25000000;
