//Important, pay attention to out of boundary problem.
run("Properties...", "channels=1 slices=1 frames=1 unit=px pixel_width=1 pixel_height=1 voxel_depth=1");

var height=getHeight();
var width=getWidth();
var deltaA=10;
var d1=1;
var centX=0;
var centY=0;
var xb,yb;
var dataTitle;
var lineTag;
var dotIndex;
var textTitle;
var saveDir;
setColor("black");
Dialog.create("selection parameters");
Dialog.addNumber("The number of line slections",deltaA);
Dialog.addNumber("The length of the slections",d1);
Dialog.addCheckbox("user input line length", false); 
Dialog.show();
deltaA=Dialog.getNumber();
d1=Dialog.getNumber();
lineTag=Dialog.getCheckbox;
setBatchMode(true);
run("Make Binary", "thresholded remaining black");
run("Restore Selection");  
dataTitle=getTitle();

dotIndex=indexOf(dataTitle,".");
if (dotIndex<0)
{ dotIndex=lengthOf(dataTitle);
}
TextTitle=substring(dataTitle,0,dotIndex)+".txt"; //creat txt for fileName
roiTitle=substring(dataTitle,0,dotIndex)+"roi.zip";
imgTitle=substring(dataTitle,0,dotIndex)+"bin.tif";
imgTitle2=substring(dataTitle,0,dotIndex)+"bin2.tif";
imgTitle3=substring(dataTitle,0,dotIndex)+"showLine.tif"; 
saveDir=getDirectory("choose a directory to save results");
saveTextName=saveDir+TextTitle;  // generate the name to save textWindow
saveRoiName=saveDir+roiTitle; //generate the name to save RROI
saveImgName=saveDir+imgTitle;// generate the name to save the new binary imag.
saveImgName2=saveDir+imgTitle2;
saveImgName3=saveDir+imgTitle3;
saveAs("tiff",saveImgName);
dataTitle=getTitle(); // re-obtain the new name of the binary imag.

var InAngle=PI*2/deltaA; // in radius

Roi.getCoordinates(xb,yb);

//setBatchMode(true);
creatLine();
showLine(height,width);  
//I can use the log window in the showLine function'
//anaLine(dataTitle);
selectWindow("Log");
saveAs("Text",saveTextName);
run("Close");
roiManager("save",saveRoiName);
 
list = getList("window.titles"); 
//    
selectWindow("Results");
run("Close"); 
saveAs("tiff",saveImgName2);


//*******************************//
function creatLine()
{sumX=0;
 sumY=0;
 maxX=0;
 maxY=0;
 d2=d1;
run("Set Measurements...", "  centroid redirect=None decimal=3");
run("Clear Results");
run("Measure");
centX=getResult('X',0);
centY=getResult('Y',0);

// start calculate d1 according to the boundary
for(i=0;i<xb.length;i++)
{ ddx=xb[i]-centX;
  ddy=yb[i]-centY;
  dc=sqrt(ddx*ddx+ddy*ddy);
  if (dc>d2)
  { d2=dc;       //d1 is the global variable, so other function can access,d2 here equalto d1
   maxX=xb[i];
   maxY=yb[i];
 }
 
}
//finish calculate d1
roiManager("reset");
setOption("show All",true);
//drawOval(centX,centY,3,3);
if (lineTag==false)
   d1=floor(d2);         //  need an integer
else 
   d1=floor(d1);
 for(i=0;i<PI;i=i+InAngle)
        {
 	xStart1=centX-d1*cos(i);
 	xStop1=centX+d1*cos(i);
 	yStart1=centY-d1*sin(i);
 	yStop1=centY+d1*sin(i);
	makeLine(xStart1,yStart1,xStop1,yStop1);
	roiManager("add");
    }
}
// ***************************************//

function showLine(height,width)
{ newImage("showLine", "8-bit",1024,1024,1);
 selectImage("showLine");
  setColor("black");
  setLineWidth(6);
  drawOval(centX,centY,3,3);
 LastI=xb.length-1;
 // start to draw the line in the result image
 for(i=1;i<xb.length;i++)
 {fi=i-1;
 drawLine(xb[fi],yb[fi],xb[i],yb[i]);
  } 
 drawLine(xb[LastI],yb[LastI],xb[0],yb[0]);
//draw the boundary in slectImage

selectImage(dataTitle);
setColor("black");
 setLineWidth(6);
for(i=1;i<xb.length;i++)
 {fi=i-1;
 drawLine(xb[fi],yb[fi],xb[i],yb[i]);
  } 
 drawLine(xb[LastI],yb[LastI],xb[0],yb[0]);
// finish drawing the line of the boundary on the binary inage
count=roiManager("count");
x=newArray(d1*2);
y=newArray(d1*2);
val=newArray(d1*2);
  for (i=0;i<count;i++)
 { selectImage(dataTitle);
   roiManager("select",i);
   Roi.getCoordinates(xPs,yPs);
   x0=xPs[0];
   y0=yPs[0];
   x1=xPs[1];
   y1=yPs[1];
   dx=x1-x0;
   dy=y1-y0;
   d=sqrt(dx*dx+dy*dy);
   ang=atan2(dy,dx);  
   for(j=0;j<(d-1);j++)
   {x[j]=round(x0+j*cos(ang));
    y[j]=round(y0+j*sin(ang)); // use round coz I need the integer as the coordiates
   val[j]=getPixel(x[j],y[j]);
    }
   //start point of show the intensity plot
    
    selectImage("showLine");  
    for(j=0;j<(d-1);j++)
    {setPixel(x[j],y[j],val[j]);
      //write("this is from show line");
      write( i+ "      " +x[j]+ "     "+y[j]+"        " +val[j]);
    }
  // stop of the show intensity plot  
   }
saveAs("tiff",saveImgName3);
close();
   
}
//**************************//
 function anaLine(img)
 { run("Clear Results");
   selectImage(img);
  // setMinAndMax(0,65535);
//run("8-bit");     // I think it is not necessary to have this. I do not understand now
s=getDirectory("choose a dir");
tt=getNumber("input for the starting number",1);
 count=roiManager("count");
 for (j=0;j<count;j++)
 {      roiManager("select",j); 
 ss=d2s(tt,0);
 roiManager("Rename",ss);
 tt=tt+1;
 v=Roi.getName();
 //name=s+v +".txt";
 name2=s+img+".txt";
  profile = getProfile();
  for (i=0; i<profile.length; i++)
     { setResult("Value", i, profile[i]);
      updateResults;}
 }
 saveAs("Results",name2);
 }
 