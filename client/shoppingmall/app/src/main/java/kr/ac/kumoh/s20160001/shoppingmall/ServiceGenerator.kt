package kr.ac.kumoh.s20160001.shoppingmall

import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class ServiceGenerator {
    var BaseURL = "http://202.31.200.237:2010"
    var Client = OkHttpClient.Builder()

    private val builder = Retrofit.Builder().baseUrl(BaseURL).addConverterFactory(GsonConverterFactory.create())

    fun <S> createService(serviceClass: Class<S>?): S {
        val retrofit = builder.client(Client.build()).build()
        return retrofit.create(serviceClass)
    }

}