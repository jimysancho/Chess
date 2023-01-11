# Chess
Chess game made with Pygame Python

## Introduction

The only library used to create this game is `Pygame`. It is a completly playable chess game, with the basic rules such as: 
* Castle: short and long
* Promotion
* Two moves for the pawns if it is their first move
* Checkmate
* Check if the king is safe
* Do not move any piece if the king is under attack or will be under attack after some move

### 1. Demo

https://user-images.githubusercontent.com/105709376/211821470-04bd819f-9f7a-4e07-a06a-c2144713d376.mov


### 2. Check situation

When one of the players gives a check, none of the pieces can move unless its movement will protect the king. 


https://user-images.githubusercontent.com/105709376/211821553-9521042f-d973-4532-8811-728d79844c29.mov


### 3. Promotion menu

When one of the players's pawn reaches the last row, a promotion menu will appear on the screen: 

<img width="554" alt="promotion_menu" src="https://user-images.githubusercontent.com/105709376/211821587-fb2b43eb-bf2b-41f5-a78c-91cc8ce2f76d.png">

In order for that pawn to "transform" to the desired piece, we only need to select the piece we want. 


https://user-images.githubusercontent.com/105709376/211821628-ed8789ba-2156-42fe-99f0-ddb4d3895690.mov


### 4. Checkmate

When one of the players manages to checkmate the oponent, a message will appear on the screen. To play again just click the `Space` key. 


https://user-images.githubusercontent.com/105709376/211821669-bb4b0d1f-74b3-452f-8b58-fc19947b74f4.mov


