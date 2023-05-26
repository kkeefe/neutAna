// electron weights on TDR
float electron_weights(float energy)
{
    if(energy >= 500  && energy < 500 + 250) return 14.8; // 500
    if(energy >= 750  && 750+250 > energy) return 25;   // 750
    if(energy >= 1000 && 1000+250 > energy) return 26;   // 1G
    if(energy >= 1250 && 1250+250 > energy) return 35;   // 1.25G
    if(energy >= 1500 && 1500+250 > energy) return 57;   // 1.5G
    if(energy >= 1750 && 1750+250 > energy) return 89;   // 1.75
    if(energy >= 2000 && 2000+250 > energy) return 110;  // 2
    if(energy >= 2250 && 2250+250 > energy) return 130;  // 2.25
    if(energy >= 2500 && 2500+250 > energy) return 135;  // 2.5
    if(energy >= 2750 && 2750+250 > energy) return 133;  // 2.75
    if(energy >= 3000 && 3000+250 > energy) return 123;  // 3
    if(energy >= 3250 && 3250+250 > energy) return 111;  // 3.25
    if(energy >= 3500 && 3500+250 > energy) return 92;  // 3.5
    if(energy >= 3750 && 3750+250 > energy) return 73;  // 3.75
    if(energy >= 4000 && 4000+250 > energy) return 58;  // 4
    if(energy >= 4250 && 4250+250 > energy) return 42;  // 4.25
    if(energy >= 4500 && 4500+250 > energy) return 30;  // 4.5
    if(energy >= 4750 && 4750+250 > energy) return 22;  // 4.75
    if(energy >= 5000 && 5000+250 > energy) return 17;  // 5
    if(energy >= 5250 && 5250+250 > energy) return 15;  // 5.25
    if(energy >= 5500 && 5500+250 > energy) return 12; // 5.5
    if(energy >= 5750 && 5750+250 > energy) return 10.5; // 5.75
    if(energy >= 6000 && 6000+250 > energy) return 10; // 6
    if(energy >= 6250 && 6250+250 > energy) return 7.5; // 6.25
    if(energy >= 6500 && 6500+250 > energy) return 7.25; // 6.5
    if(energy >= 6750 && 6750+250 > energy) return 6.5; // 6.75
    if(energy >= 7000 && 7000+250 > energy) return 6.4; // 7
    if(energy >= 7250 && 7250+250 > energy) return 6.0; // 7.25
    if(energy >= 7500 && 7500+250 > energy) return 6.0; // 7.5
    if(energy >= 7750 && 7750+250 > energy) return 6.0; // 7.75
    return 0;
}

float aelectron_weights(float energy)
{
    if(energy >= 500  && 500+250 > energy) return 6.2; // 500
    if(energy >= 750  && 750+250 > energy) return 11.1;   // 750
    if(energy >= 1000 && 1000+250 > energy) return 13;   // 1G
    if(energy >= 1250 && 1250+250 > energy) return 11.6;   // 1.25G
    if(energy >= 1500 && 1500+250 > energy) return 14;   // 1.5G
    if(energy >= 1750 && 1750+250 > energy) return 19;   // 1.75
    if(energy >= 2000 && 2000+250 > energy) return 26;  // 2
    if(energy >= 2250 && 2250+250 > energy) return 31.8;  // 2.25
    if(energy >= 2500 && 2500+250 > energy) return 37.1;  // 2.5
    if(energy >= 2750 && 2750+250 > energy) return 37.6;  // 2.75
    if(energy >= 3000 && 3000+250 > energy) return 37.2;  // 3
    if(energy >= 3250 && 3250+250 > energy) return 34.9;  // 3.25
    if(energy >= 3500 && 3500+250 > energy) return 32.9;  // 3.5
    if(energy >= 3750 && 3750+250 > energy) return 25.7;  // 3.75
    if(energy >= 4000 && 4000+250 > energy) return 22.3;  // 4
    if(energy >= 4250 && 4250+250 > energy) return 17.2;  // 4.25
    if(energy >= 4500 && 4500+250 > energy) return 14.9;  // 4.5
    if(energy >= 4750 && 4750+250 > energy) return 11.1;  // 4.75
    if(energy >= 5000 && 5000+250 > energy) return 10;  // 5
    if(energy >= 5250 && 5250+250 > energy) return 9.7;  // 5.25
    if(energy >= 5500 && 5500+250 > energy) return 8.1; // 5.5
    if(energy >= 5750 && 5750+250 > energy) return 6.7; // 5.75
    if(energy >= 6000 && 6000+250 > energy) return 6.2; // 6
    if(energy >= 6250 && 6250+250 > energy) return 6; // 6.25
    if(energy >= 6500 && 6500+250 > energy) return 5.8; // 6.5
    if(energy >= 6750 && 6750+250 > energy) return 5.2; // 6.75
    if(energy >= 7000 && 7000+250 > energy) return 5.4; // 7
    if(energy >= 7250 && 7250+250 > energy) return 5.0; // 7.25
    if(energy >= 7500 && 7500+250 > energy) return 5.2; // 7.5
    if(energy >= 7750 && 7750+250 > energy) return 5.0; // 7.75
    return 0;
}

float muon_weights(float energy)
{
    if(energy >= 500  && 500+250 > energy) return 132; 
    if(energy >= 750  && 750+250 > energy) return 235;   
    if(energy >= 1000 && 1000+250 > energy) return 520;   
    if(energy >= 1250 && 1250+250 > energy) return 718;   
    if(energy >= 1500 && 1500+250 > energy) return 632;   
    if(energy >= 1750 && 1750+250 > energy) return 444;   
    if(energy >= 2000 && 2000+250 > energy) return 280;  
    if(energy >= 2250 && 2250+250 > energy) return 183;  
    if(energy >= 2500 && 2500+250 > energy) return 160;  
    if(energy >= 2750 && 2750+250 > energy) return 181;  
    if(energy >= 3000 && 3000+250 > energy) return 220;  
    if(energy >= 3250 && 3250+250 > energy) return 260;  
    if(energy >= 3500 && 3500+250 > energy) return 286;  
    if(energy >= 3750 && 3750+250 > energy) return 282;  
    if(energy >= 4000 && 4000+250 > energy) return 275;  
    if(energy >= 4250 && 4250+250 > energy) return 245;  
    if(energy >= 4500 && 4500+250 > energy) return 220;  
    if(energy >= 4750 && 4750+250 > energy) return 190;  
    if(energy >= 5000 && 5000+250 > energy) return 160;  
    if(energy >= 5250 && 5250+250 > energy) return 144;  
    if(energy >= 5500 && 5500+250 > energy) return 135; 
    if(energy >= 5750 && 5750+250 > energy) return 125; 
    if(energy >= 6000 && 6000+250 > energy) return 118; 
    if(energy >= 6250 && 6250+250 > energy) return 115; 
    if(energy >= 6500 && 6500+250 > energy) return 114; 
    if(energy >= 6750 && 6750+250 > energy) return 100; 
    if(energy >= 7000 && 7000+250 > energy) return 101; 
    if(energy >= 7250 && 7250+250 > energy) return 95; 
    if(energy >= 7500 && 7500+250 > energy) return 96; 
    if(energy >= 7750 && 7750+250 > energy) return 95; 
    return 0;
}

float amuon_weights(float energy)
{
    if(energy >= 500  && 500+250 > energy) return 42; 
    if(energy >= 750  && 750+250 > energy) return 88;   
    if(energy >= 1000 && 1000+250 > energy) return 196;   
    if(energy >= 1250 && 1250+250 > energy) return 288;   
    if(energy >= 1500 && 1500+250 > energy) return 267;   
    if(energy >= 1750 && 1750+250 > energy) return 191;   
    if(energy >= 2000 && 2000+250 > energy) return 128;  
    if(energy >= 2250 && 2250+250 > energy) return 83;  
    if(energy >= 2500 && 2500+250 > energy) return 74;  
    if(energy >= 2750 && 2750+250 > energy) return 84;  
    if(energy >= 3000 && 3000+250 > energy) return 110;  
    if(energy >= 3250 && 3250+250 > energy) return 132;  
    if(energy >= 3500 && 3500+250 > energy) return 150;  
    if(energy >= 3750 && 3750+250 > energy) return 155;  
    if(energy >= 4000 && 4000+250 > energy) return 154;  
    if(energy >= 4250 && 4250+250 > energy) return 147;  
    if(energy >= 4500 && 4500+250 > energy) return 135;  
    if(energy >= 4750 && 4750+250 > energy) return 121;  
    if(energy >= 5000 && 5000+250 > energy) return 112;  
    if(energy >= 5250 && 5250+250 > energy) return 105;  
    if(energy >= 5500 && 5500+250 > energy) return 98; 
    if(energy >= 5750 && 5750+250 > energy) return 92; 
    if(energy >= 6000 && 6000+250 > energy) return 88; 
    if(energy >= 6250 && 6250+250 > energy) return 85; 
    if(energy >= 6500 && 6500+250 > energy) return 81; 
    if(energy >= 6750 && 6750+250 > energy) return 78; 
    if(energy >= 7000 && 7000+250 > energy) return 75.5; 
    if(energy >= 7250 && 7250+250 > energy) return 70; 
    if(energy >= 7500 && 7500+250 > energy) return 72; 
    if(energy >= 7750 && 7750+250 > energy) return 69; 
    return 0;
}