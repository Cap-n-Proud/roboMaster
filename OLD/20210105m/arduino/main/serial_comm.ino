//Now the command list must be defined https://github.com/CreativeRobotics/Commander/blob/master/examples/BasicCommands/masterCommands.ino
const commandList_t commands[] = {
  {
    "statusReport",
    TelemetryTXJSON,
    "Say goodbye"
  },
  {
    "setLightRGB",
    setLightRGB,
    "Set color of the LED"
  },
  {
    "pumpStart",
    pumpStart,
    "Start pumps and run for X minutes"
  },
  {
    "pumpStop",
    pumpStop,
    "Stop pump"
  },
  {
    "setBrightness",
    setBrightness,
    "Set brightness"
  },
};

// pumpStart
// pumpStop
// setBrightness
// setRGB
// printSysInfo

//setBrightness 43
//setLightRGB 255 255 255
//statusReport

//Initialisation function
void initialiseCommander() {
  cmd.begin( & Serial, commands, sizeof(commands)); //start Commander on Serial
  cmd.commandPrompt(OFF); //enable the command prompt
  cmd.echo(false);     //Echo incoming characters to theoutput port
  cmd.errorMessages(ON); //error messages are enabled - it will tell us if we issue any unrecognised commands
  cmd.autoChain(ON);
}

bool pumpStop(Commander & Cmdr) {
  // Here code to swith the pump on
  pumpON = false;
  Cmdr.println(pumpON);
  Cmdr.println("Pump stoppped");
  return 0;
}

bool pumpStart(Commander & Cmdr) {
  long myInt;
  if (Cmdr.getInt(myInt)) {
    //Cmdr.print("Pump timer set to: ");
    //Cmdr.println(myInt);
    pumpON = true;
    timer.in(myInt * 1000 * 60, pumpStop);
    //sendInfo(String("Pump started for: ") + myInt + String(" minutes"));
  }

  return 0;
}

bool setBrightness(Commander & Cmdr) {
  // Here code to swith the pump on
  int myInt;

  if (Cmdr.getInt(myInt)) {
    Brightness = myInt;
      } else Cmdr.println("Operation failed");
  TelemetryTXJSON();
  return 0;

}

bool setLightRGB(Commander & Cmdr) {
  //create an array to store any values we find
  int values[3] = {0,0,0};
  for (int n = 0; n < 3; n++) {
    //try and unpack an int, if it fails there are no more left so exit the loop
    if (Cmdr.getInt(values[n])) {

    } else break;
  }
  //print it out
  String pRGB = "";
  for (int n = 0; n < 3; n++) {
    pRGB = pRGB + String(values[n]) + String(" ");
  }
  RGB = pRGB;
  //Cmdr.print("LED set to RGB: " + pRGB);
  return 0;
}

bool setIntsHandler(Commander &Cmdr){
  //create an array to store any values we find
  int values[4] = {0,0,0,0};

  int itms = Cmdr.countItems();
  Cmdr.print("There are ");
  Cmdr.print(itms);
  Cmdr.println(" items in the payload");
  
  for(int n = 0; n < 4; n++){
    //try and unpack an int, if it fails there are no more left so exit the loop
    if(Cmdr.getInt(values[n])){
      Cmdr.print("unpacked ");
      Cmdr.println(values[n]);
    }else break;
  }
  //print it out
  Cmdr.println("Array contents after processing:");
  String pRGB = "";
  for(int n = 0; n < 4; n++){
    Cmdr.print(n);
    Cmdr.print(" = ");
    Cmdr.println(values[n]);
      pRGB = pRGB + String(values[n]) + String(" ");
    RGB = pRGB;
  }
  //Cmdr.chain();
  //Cmdr.printDiagnostics();
  return 0;
}
bool TelemetryTX() { // for help on dtostrf http://forum.arduino.cc/index.php?topic=85523.0

  String line = "";
  String telemMarker = "T";
  //Need to calculate parameters here because the main loop has a different frequency
  //TxLoopTime = millis() - TxLoopTime;

  line = telemMarker + SEPARATOR +
    String(pumpON) + SEPARATOR +
    String(RGB[0]) + " " + String(RGB[1]) + " " + String(RGB[2]) + SEPARATOR +
    String(Brightness) + SEPARATOR +
    String((float(random(1000, 9999)) / 100)) + SEPARATOR +

    String(info) + SEPARATOR;
  Serial.println(line);

  /*line = "T" + SEPARATOR
         + yaw + SEPARATOR
         + pitch + SEPARATOR
         + roll + SEPARATOR
         + heading + SEPARATOR
         + Info
    //+ SEPARATOR
    //+ LastEvent;*/
  //Serial.println(line);
  return 0;

}
//
//bool TelemetryTXJSONLIB(Commander & Cmdr) { // for help on dtostrf http://forum.arduino.cc/index.php?topic=85523.0
//  //{"type": "I", "pumpON":1,"RGB": "20 255 30","brightness":80} 
//    delay(100);
//  StaticJsonDocument < 400 > line;
//  line["type"] = "T";
//  line["pumpON"] = pumpON;
//  line["RGB"] = String(RGB);
//  line["brightness"] = Brightness;
//  line["PH"] = "0";
//  line["waterLevel"] = "0";
//  serializeJson(line, Serial);
//  Serial.println();
//  //size calculated here: https://arduinojson.org/v6/assistant/
//return 0;
//}
//
bool TelemetryTXJSON() //statusReport
{ // for help on dtostrf http://forum.arduino.cc/index.php?topic=85523.0
  //{"type": "I", "pumpON":1,"RGB": "20 255 30","brightness":80} 
  delay(100);
  String line, line2, line3;
  line = String("{\"type\":") + String("\"T\",") + "\"pumpON\":" + pumpON + ",\"RGB\":" + "\"" + String(RGB) + "\"" + ",\"brightness\":" + Brightness + "}";
  Serial.println(line);
  return 0;
}
//
//

//Initialisation function
void initTimer() {
  //timer.every(1 * 1000, toggle_led);
  timer.every(0.5  * 1000, TelemetryTXJSON);

}
