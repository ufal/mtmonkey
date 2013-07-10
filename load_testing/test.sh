#!/bin/bash

echo en - cs
./test.pl en cs 'I have lung cancer.'
echo cs - en
./test.pl cs en 'Mám rakovinu plic.'

echo en - de
./test.pl en de 'I have lung cancer.'
echo de - en
./test.pl de en 'Ich habe Lungenkrebs.'

echo en - fr
./test.pl en fr 'I have lung cancer.'
echo fr - en
./test.pl fr en "J' ai le cancer du poumon."

