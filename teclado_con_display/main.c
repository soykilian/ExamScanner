#include <wiringPi.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>

#include "tm1637.h"

#define ROWS 4
#define COLS 4

#define wPI_ROW_1 7
#define wPI_ROW_2 26
#define wPI_ROW_3 2
#define wPI_ROW_4 3

#define wPI_COL_1 22
#define wPI_COL_2 23
#define wPI_COL_3 27
#define wPI_COL_4 25

#define wPI_CLK 21
#define wPI_DIO 31

#define DISPLAY_DIGITS 4
#define LOOP_DELAY 300

int contador = 0;
char pressedKey = '\0';
int rowPins[ROWS] = {wPI_ROW_1, wPI_ROW_2, wPI_ROW_3, wPI_ROW_4};
int colPins[COLS] = {wPI_COL_1, wPI_COL_2, wPI_COL_3, wPI_COL_4};

char keys[ROWS][COLS] = {
   {'1', '2', '3', 'A'},
   {'4', '5', '6', 'B'},
   {'7', '8', '9', 'C'},
   {'*', '0', '#', 'D'}
};


double buscar_nota_en_CSV(char* DNI);
char* getfield(char* line, int num);

char* DNI;
char* NOTA;

void signaux(int sigtype) {
  TMclear();
	exit(0);
}

void init_keypad() {
   for (int c = 0; c < COLS; c++) {
      pinMode(colPins[c], OUTPUT);
      digitalWrite(colPins[c], HIGH);
   }

   for (int r = 0; r < ROWS; r++) {
      pinMode(rowPins[r], INPUT);
      pullUpDnControl(rowPins[r], PUD_UP);
   }
}

int findLowRow() {
   for (int r = 0; r < ROWS; r++) {
      if (digitalRead(rowPins[r]) == LOW)
         return r;
   }

   return -1;
}

char get_key() {
   int rowIndex;

   for (int c = 0; c < COLS; c++) {
      digitalWrite(colPins[c], LOW);

      rowIndex = findLowRow();
      if (rowIndex > -1) {
         if (!pressedKey)
            pressedKey = keys[rowIndex][c];
         return pressedKey;
      }

      digitalWrite(colPins[c], HIGH);
   }

   pressedKey = '\0';

   return pressedKey;
}

int main(void) {
   wiringPiSetup();
   init_keypad();

   DNI = strdup("");
   NOTA = strdup("");

   signal(SIGINT,signaux);
   signal(SIGTERM,signaux);
   TMsetup(wPI_CLK, wPI_DIO);
   TMsetBrightness(7);

   TMshowDouble(88.88);

   while(1)
   {
      char x = get_key();

      if (x) {
        strncat(DNI, &x, 1);
        printf("DNI hasta el momento: %s\n", DNI);

        if (strstr(DNI, "#") == NULL) {
    		    double dni_mostrado = strtod(DNI, NULL);
            //Mostrar los últimos DISPLAY_DIGITS del DNI en display
	          contador++;
	          if(contador > DISPLAY_DIGITS)
                contador = DISPLAY_DIGITS;
	          char* substr = malloc(contador);
	          strncpy(substr, DNI+(strlen(DNI)-contador), contador);
            int dni_display = atoi(substr);
    			  TMshowNumber(dni_display, 0, false, DISPLAY_DIGITS, 0);
    		}

    		if (strstr(DNI, "#") != NULL) {
    			double nota = buscar_nota_en_CSV(DNI);
    			printf("Valor de nota: %f\n", nota);
    			TMshowDouble(nota);
    			strcpy(DNI, "");
          contador = 0;
    		}

      }

      delay(LOOP_DELAY); //Detiene el programa antes de seguir comprobando teclas
   }

   return 0;
}


char* getfield(char* line, int num) {
    const char* tok;
    for (tok = strtok(line, ",");
            tok && *tok;
            tok = strtok(NULL, ",\n"))
    {
        if (!--num)
            return tok;
    }
    return NULL;
}


//https://stackoverflow.com/questions/12911299/read-csv-file-in-c
double buscar_nota_en_CSV(char* DNI) {
  FILE* stream = fopen("../data.csv", "r");
  DNI[strlen(DNI)-1] = '\0';

  char line[1024];
  while (fgets(line, 1024, stream))
  {
      char* tmp = strdup(line);

      char* DNI_CSV = getfield(tmp, 1);

      if(strcmp(DNI_CSV, DNI) == 0) {
        char* tmp2 = strdup(line);
        NOTA = getfield(tmp2, 5);
      	// printf("nota: %s", NOTA);
        free(tmp2);
      }

      // NOTE strtok clobbers tmp
      free(tmp);
  }

  return strtod(NOTA, NULL);

}
