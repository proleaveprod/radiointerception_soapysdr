# Radio interception of RC model by using LimeSDR and SoapySDR python module

Recently, the technologies of SDR are becoming increasingly applied. The development of SDR and its availability allow us to develop our own software and hardware complexes, including using SDR to intercept radio control. 

In the fall of 2022, our university team participated in the RadioFest  competition, one of the directions of which was "Radio Model Control Interception", which became the basis of this scientific work. This direction included the recognition and interception of the radio signal that controls the bulldozer model. 
After that, competitors had to write an algorithm to control the bulldozer using broadcasting from LimeSDR board. Each team was provided with equipment: a circular antenna,  LimeSDR transceiver, Raspberry PI 4 with  Dragons_Pi operating system
![image](https://user-images.githubusercontent.com/45439167/218255315-47dd19b0-a0fa-4028-bf7e-790a84ff3a3f.png)
![image](https://user-images.githubusercontent.com/45439167/218255372-e7cec2e0-e62e-4fd3-bb61-92e69f7b2d08.png)


<t1>How it works</t1>
The developed script works according to the following algorithm:
1. Signals are saved in wav format.
2. The script loads the files and converts the values(вальюс) into an array 
3. The script connects to LimeSDR via the "SoapySDR" library.
4. The script transmits the corresponding command to LimeSDR for broadcasting at a given radio frequency.

In addition, in order to avoid receiving the enemy’s signal, it was decided to add pseudo(сюдо)-sequence broadcasting with headers. This played a great advantage for our team, since such a signal stopped the operation of the enemy model.

Thus, a program was implemented to intercept the radio model control, repeating the entire radio model controller. The task set limited the available means for its implementation, namely: it was possible to use only the GNURadio and the Python language. In the course of solving the problem using the GNURadio, the upper-level structureof the model was determined and an attempt was made to use it in practice. However, this attempt was unsuccessful and it was decided to implement the functionality through python-script. As a result, the developed script made it possible to perform all the necessary actions, removed the delay of 5 seconds and reduced it to 500 milliseconds ping. 
