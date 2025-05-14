# RL_PID
ReInforcement Learning application for PID autotuning


## Scope
The scope of this optimization algorithm is to showcase a simple Re-Inforcement Learning Application for control purpuse.
A simple but common system model is used, which typically is being controlled by a PID controller.

One of the biggest challenges of calibrating a PID controller is, that some of the plant parameters like mass or temperature change dramatically during its runtime.
A well calibrated PID shall be stable at any time and shall have a smooth behavior with low or without overshoot.

A further special challenge in calibrating a PID controller on a real system is, that - in opposite to MiL tuning - everytime there are different boundary conditions.
This is exactly the use-case for RL.

## Implementation

The shown script calibrates the example system by utilization of a RL approach.
For each validation step a batch of 10-50 swing-in trials is performed.

For exploration, the parameters are changed randomly.
The reward is the negative sum of losses minus a penalty for overshoots.

## Result

After a long trial period, the loss and the overshoot becomes really low.
And this becomes even superhuman, as I also tried a manual PID calibration, but with a slightly worse reward (Ok, I took much less exploration)
However, the script just shows the feasibility for RL on random data, where repetition and gradient calculation is not possible.

