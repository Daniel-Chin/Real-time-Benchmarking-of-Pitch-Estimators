/* R2D2 Pitch Processing
 *
 * Audio analysis for pitch extraction 
 *
 * Relies on Minim audio library
 * http://code.compartmental.net/tools/minim/
 *
 * L. Anton-Canalis (info@luisanton.es)
 */

import processing.opengl.*;

import javax.swing.JFileChooser;

import ddf.minim.analysis.*;
import ddf.minim.effects.*;
import ddf.minim.signals.*;
import ddf.minim.*;

// PitchDetectorAutocorrelation PD; //Autocorrelation
PitchDetectorHPS PD; //Harmonic Product Spectrum -not working yet-
// PitchDetectorFFT PD; // Naive
AudioSource AS;
Minim minim;

//Some arrays just to smooth output frequencies with a simple median.
float []freq_buffer = new float[10];
float []sorted;
int freq_buffer_index = 0;

long last_t = -1;
float avg_level = 0;
float last_level = 0;
String filename;
float begin_playing_time = -1;

void setup()
{
  size(1000, 800);
  minim = new Minim(this);
  minim.debugOn();

  AS = new AudioSource(minim);

  /*
  // Choose .wav file to analyze
  boolean ok = false;
  while (!ok) {
    JFileChooser chooser = new JFileChooser();
    chooser.setFileFilter(chooser.getAcceptAllFileFilter());
    int returnVal = chooser.showOpenDialog(null);
    if (returnVal == JFileChooser.APPROVE_OPTION) {
    filename = chooser.getSelectedFile().getPath();
      AS.OpenAudioFile(chooser.getSelectedFile().getPath(), 5, 512); //1024 for AMDF
      ok = true;
    }
  }
  */

  // Comment the previous block and uncomment the next line for microphone input
  AS.OpenMicrophone();

  // PD = new PitchDetectorFFT();
  // PD.ConfigureFFT(2048, AS.GetSampleRate());
  // PD = new PitchDetectorAutocorrelation();  //This one uses Autocorrelation
  PD = new PitchDetectorHPS(); //This one uses Harmonit Product Spectrum -not working yet-
  PD.SetSampleRate(AS.GetSampleRate());
  AS.SetListener(PD);

  rectMode(CORNERS);
  textAlign(LEFT, CENTER);
  textSize(18);
  fill(0);
  stroke(255);
}

int page = -1;

void draw()
{
  if (begin_playing_time == -1)
    begin_playing_time = millis();

  float f = 0;
  float level = AS.GetLevel();
  long t = PD.GetTime();
  if (t == last_t) return;
  last_t = t;
  int xpos = (int)t - page * width;
  if (xpos >= width-1) {
    page ++;
    drawBack();
  }

  f = PD.GetFrequency();

  /*freq_buffer[freq_buffer_index] = f;
  freq_buffer_index++;
  freq_buffer_index = freq_buffer_index % freq_buffer.length;
  sorted = sort(freq_buffer);

  f = sorted[5];*/

  stroke(level * 255.0 * 10.0);
  pushMatrix();
  translate(0, height);
  scale(1, -1);
  float y = freq2Y(f);
  print("freq ");
  print(f);
  // print("; y ");
  // print(y);
  println();
  line(xpos, 0, xpos, y * height);
  popMatrix();

  avg_level = level;
  last_level = f;
}

float freq2Y(float freq) {
  return (log(freq) - 4.1) / 3f;
}

void stop()
{
  AS.Close();

  minim.stop();

  println("Se acabo");

  super.stop();
}

final static String NOTES = "CDEFGAB";
void drawBack() {
  fill(255);
  background(0);
  pushMatrix();
  translate(0, height);
  for (int i = 36; i < 84; i ++) {
    int chroma = i % 12;
    boolean is_diatonic;
    char diatone = '_';
    if (chroma < 5) {
      is_diatonic = (chroma % 2) == 0;
      if (is_diatonic) {
        diatone = NOTES.charAt(round(chroma / 2f));
      }
    } else {
      is_diatonic = (chroma % 2) == 1;
      if (is_diatonic) {
        diatone = NOTES.charAt(ceil(chroma / 2f));
      }
    }
    float y = - freq2Y(exp((i - 60) * 0.057762265046662105 + 5.566914341492348)) * height;
    // if (is_diatonic) {
    //   stroke(255);
    //   text(diatone, 10, y);
    // } else {
    //   stroke(100);
    // }
    if (chroma == 0) {
      stroke(255);
    } else {
      stroke(100);
    }
    line(30, y, width, y);
  }
  popMatrix();
}
