package kr.ac.kumoh.s20160001.shoppingmall.fragment

import android.net.Uri
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import kr.ac.kumoh.s20160001.shoppingmall.R


class sendFragment : Fragment() {
    lateinit var imageUri: Uri

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            imageUri = Uri.parse(it.getString("Uri"))
        }
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?,
                              savedInstanceState: Bundle?): View? {
        val v = inflater.inflate(R.layout.fragment_send, container, false)
        val viewer = v.findViewById<ImageView>(R.id.selectedImg)
        viewer.setImageURI(imageUri)

        return v
    }


}