package com.rust.samples;


class MyClassLoader extends ClassLoader {

  @Override
  public Class<?> defineMyClass(byte[]b,int off,int len){

    return super.defineMyClass(b,off,len);

  }

}
